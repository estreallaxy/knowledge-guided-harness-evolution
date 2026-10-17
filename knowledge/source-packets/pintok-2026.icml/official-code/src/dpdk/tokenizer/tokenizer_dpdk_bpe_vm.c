// tokenizer_dpdk_bpe_vm.c - DPDK-based BPE tokenizer optimized for VM environments
#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/uio.h>
#include <sched.h>
#include <pthread.h>
#include <errno.h>
#include <ctype.h>
#include <arpa/inet.h>
#include <rte_eal.h>
#include <rte_mbuf.h>
#include <rte_mempool.h>
#include <rte_cycles.h>
#include <rte_malloc.h>
#include "bpe_util.h"
#include "vocab_util.h"

#define LISTEN_PORT    6000
#define NUM_MBUFS      8191
#define MBUF_CACHE_SIZE 250
#define MAX_CHUNKS     1000
#define MAX_TEXT_SIZE  (MAX_CHUNKS * 1200)
#define BUFFER_SIZE    65536
#define RECV_BATCH     16

// --- Shared memory for zero-copy token ID access ---
#define SHM_MAGIC 0x544F4B53u /* 'TOKS' */
struct token_shm_header {
    uint32_t magic;               // SHM_MAGIC
    uint32_t version;             // seqlock version: even=stable, odd=writer active
    uint32_t num_tokens;          // number of valid tokens
    uint32_t message_id;          // message id if extended header used (else 0)
    uint64_t packet_arrival_tsc;  // timing info (first pkt for message)
    uint64_t assembly_start_tsc;  // timing info
    uint64_t tokenize_start_tsc;  // timing info
    uint64_t tokenize_end_tsc;    // timing info
};

struct token_shm {
    struct token_shm_header *hdr;
    int fd;
    size_t size;
    char name[128];
    void *base;
};

static struct token_shm g_shm = {0};

static int shm_init(size_t max_tokens)
{
    const char *env_name = getenv("DPDK_SHM_NAME");
    const char *name = env_name && env_name[0] ? env_name : NULL;
    if (!name) {
        // Default to unique name per process
        snprintf(g_shm.name, sizeof(g_shm.name), "/dpdk_tokids_%d", (int)getpid());
        name = g_shm.name;
    } else {
        snprintf(g_shm.name, sizeof(g_shm.name), "%s", name);
    }

    size_t header_size = sizeof(struct token_shm_header);
    size_t data_size = max_tokens * sizeof(int32_t);
    g_shm.size = header_size + data_size;

    // Create POSIX SHM object with broad perms so parent (non-root) can map
    int fd = shm_open(name, O_CREAT | O_RDWR, 0666);
    if (fd < 0) {
        perror("shm_open failed");
        return -1;
    }
    if (ftruncate(fd, (off_t)g_shm.size) != 0) {
        perror("ftruncate failed");
        close(fd);
        shm_unlink(name);
        return -1;
    }
    void *addr = mmap(NULL, g_shm.size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (addr == MAP_FAILED) {
        perror("mmap failed");
        close(fd);
        shm_unlink(name);
        return -1;
    }
    g_shm.fd = fd;
    g_shm.base = addr;
    g_shm.hdr = (struct token_shm_header *)addr;

    // Initialize header
    memset(g_shm.base, 0, g_shm.size);
    g_shm.hdr->magic = SHM_MAGIC;
    g_shm.hdr->version = 0;
    g_shm.hdr->num_tokens = 0;
    g_shm.hdr->message_id = 0;

    // Announce to stdout so Python can map the region
    // Provide both the POSIX shm name and the /dev/shm path for convenience
    char dev_path[256];
    const char *name_noslash = name[0] == '/' ? name + 1 : name;
    snprintf(dev_path, sizeof(dev_path), "/dev/shm/%s", name_noslash);
    printf("SHM_READY name=%s path=%s size=%zu max_tokens=%d\n", name, dev_path, g_shm.size, (int)max_tokens);
    fflush(stdout);
    return 0;
}

static void shm_cleanup(void)
{
    if (g_shm.base && g_shm.base != MAP_FAILED) {
        munmap(g_shm.base, g_shm.size);
        g_shm.base = NULL;
    }
    if (g_shm.fd >= 0) {
        close(g_shm.fd);
        g_shm.fd = -1;
    }
    if (g_shm.name[0]) {
        // Unlink to cleanup
        shm_unlink(g_shm.name);
        g_shm.name[0] = '\0';
    }
}

static inline int *shm_tokens_ptr(void)
{
    return (int *)((uint8_t *)g_shm.base + sizeof(struct token_shm_header));
}

static inline void shm_publish_tokens(const int *token_ids, int num_tokens,
                                      uint32_t message_id,
                                      uint64_t packet_arrival_tsc,
                                      uint64_t assembly_start_tsc,
                                      uint64_t tokenize_start_tsc,
                                      uint64_t tokenize_end_tsc)
{
    if (!g_shm.hdr) return;
    // Seqlock: bump to odd, write, then bump to even
    uint32_t v = g_shm.hdr->version;
    g_shm.hdr->version = v + 1; // odd => writer active
    // metadata
    g_shm.hdr->num_tokens = (uint32_t)num_tokens;
    g_shm.hdr->message_id = message_id;
    g_shm.hdr->packet_arrival_tsc = packet_arrival_tsc;
    g_shm.hdr->assembly_start_tsc = assembly_start_tsc;
    g_shm.hdr->tokenize_start_tsc = tokenize_start_tsc;
    g_shm.hdr->tokenize_end_tsc = tokenize_end_tsc;
    // copy tokens into shared buffer
    int *dst = shm_tokens_ptr();
    if (num_tokens > 0) {
        memcpy(dst, token_ids, (size_t)num_tokens * sizeof(int));
    }
    __sync_synchronize(); // full memory barrier
    g_shm.hdr->version = v + 2; // even => stable
}

// Structure to store received chunks
struct chunk_data {
    char data[1200];
    int length;
    int received;
};

static struct chunk_data chunks[MAX_CHUNKS];
static uint32_t max_chunk_received = 0;
static uint32_t total_chunks_expected = 0;
static uint32_t received_chunks_count = 0;
static uint64_t tsc_hz = 0;
// Cache counters delta tracking
static uint64_t prev_cache_lookups = 0;
static uint64_t prev_cache_hits = 0;
static uint64_t prev_cache_inserts = 0;
static uint64_t prev_cache_insert_fails = 0;
static uint64_t prev_cache_skip_longkey = 0;
static uint64_t prev_cache_skip_oversize = 0;

// Extended mode support: multiple in-flight messages keyed by message_id
#define MAX_INFLIGHT 64
struct message_ctx {
    uint32_t message_id;
    int active;
    struct chunk_data chunks[MAX_CHUNKS];
    uint32_t max_chunk_received;
    uint32_t total_chunks_expected;
    uint32_t received_chunks_count;
    uint64_t first_arrival_tsc;
};
static struct message_ctx inflight[MAX_INFLIGHT];

// --- Isolation helpers ---
static int parse_cpu_list_has(const char* spec, int cpu) {
    if (!spec) return 0;
    const char* p = spec;
    while (*p) {
        while (*p == ' ' || *p == '\t' || *p == ',') p++;
        if (!*p) break;
        char buf[32]; int bi = 0;
        while (*p && *p != ',' && *p != ' ' && *p != '\t' && bi < (int)sizeof(buf)-1) buf[bi++] = *p++;
        buf[bi] = '\0';
        if (bi > 0) {
            int a = -1, b = -1;
            char *dash = strchr(buf, '-');
            if (dash) {
                *dash = '\0';
                if (buf[0] && dash[1] && isdigit((unsigned char)buf[0]) && isdigit((unsigned char)dash[1])) {
                    a = atoi(buf);
                    b = atoi(dash+1);
                    if (a <= b && cpu >= a && cpu <= b) return 1;
                }
            } else if (isdigit((unsigned char)buf[0])) {
                a = atoi(buf);
                if (cpu == a) return 1;
            }
        }
    }
    return 0;
}

static int is_cpu_isolated(int cpu) {
    // Try sysfs first
    FILE* f = fopen("/sys/devices/system/cpu/isolated", "r");
    if (f) {
        char line[256] = {0};
        size_t n = fread(line, 1, sizeof(line)-1, f);
        fclose(f);
        if (n > 0) {
            if (parse_cpu_list_has(line, cpu)) return 1;
        }
    }
    // Fallback: /proc/cmdline isolcpus=
    f = fopen("/proc/cmdline", "r");
    if (f) {
        char cmd[2048] = {0};
        size_t n = fread(cmd, 1, sizeof(cmd)-1, f);
        fclose(f);
        if (n > 0) {
            const char* key = "isolcpus=";
            char* pos = strstr(cmd, key);
            if (pos) {
                pos += (int)strlen(key);
                char* end = strchr(pos, ' ');
                if (!end) end = cmd + strlen(cmd);
                char val[512] = {0};
                size_t len = (size_t)(end - pos);
                if (len >= sizeof(val)) len = sizeof(val)-1;
                memcpy(val, pos, len); val[len] = '\0';
                char cleaned[512] = {0};
                size_t ci = 0;
                for (size_t i = 0; i < strlen(val) && ci < sizeof(cleaned)-1; i++) {
                    char c = val[i];
                    if (isdigit((unsigned char)c) || c == '-' || c == ',') cleaned[ci++] = c;
                    else if (c == ' ') break;
                }
                cleaned[ci] = '\0';
                if (parse_cpu_list_has(cleaned, cpu)) return 1;
            }
        }
    }
    return 0;
}

static void reset_message_ctx(struct message_ctx *m) {
    if (!m) return;
    for (uint32_t i = 0; i <= m->max_chunk_received && i < MAX_CHUNKS; i++) {
        m->chunks[i].received = 0;
        m->chunks[i].length = 0;
    }
    m->max_chunk_received = 0;
    m->total_chunks_expected = 0;
    m->received_chunks_count = 0;
    m->first_arrival_tsc = 0;
    m->message_id = 0;
    m->active = 0;
}

static struct message_ctx* get_or_alloc_ctx(uint32_t message_id, uint32_t total_chunks) {
    for (int i = 0; i < MAX_INFLIGHT; i++) {
        if (inflight[i].active && inflight[i].message_id == message_id) return &inflight[i];
    }
    for (int i = 0; i < MAX_INFLIGHT; i++) {
        if (!inflight[i].active) {
            reset_message_ctx(&inflight[i]);
            inflight[i].active = 1;
            inflight[i].message_id = message_id;
            inflight[i].total_chunks_expected = total_chunks;
            return &inflight[i];
        }
    }
    // Evict slot 0 if all busy
    reset_message_ctx(&inflight[0]);
    inflight[0].active = 1;
    inflight[0].message_id = message_id;
    inflight[0].total_chunks_expected = total_chunks;
    return &inflight[0];
}

// Parse header supporting legacy (8 bytes: seq,total) and extended ("TOKN"+seq+total+msg_id)
static int parse_chunk_header(const char *buffer, ssize_t received,
                              uint32_t *seq_num, uint32_t *total_chunks,
                              uint32_t *message_id, int *is_extended,
                              int *header_len) {
    if (received < 8) return -1;
    if (received >= 16 && buffer[0]=='T' && buffer[1]=='O' && buffer[2]=='K' && buffer[3]=='N') {
        *seq_num = ((uint32_t)(unsigned char)buffer[4] << 24) |
                   ((uint32_t)(unsigned char)buffer[5] << 16) |
                   ((uint32_t)(unsigned char)buffer[6] << 8) |
                   ((uint32_t)(unsigned char)buffer[7]);
        *total_chunks = ((uint32_t)(unsigned char)buffer[8] << 24) |
                        ((uint32_t)(unsigned char)buffer[9] << 16) |
                        ((uint32_t)(unsigned char)buffer[10] << 8) |
                        ((uint32_t)(unsigned char)buffer[11]);
        *message_id = ((uint32_t)(unsigned char)buffer[12] << 24) |
                      ((uint32_t)(unsigned char)buffer[13] << 16) |
                      ((uint32_t)(unsigned char)buffer[14] << 8) |
                      ((uint32_t)(unsigned char)buffer[15]);
        *is_extended = 1;
        // Header for extended mode is exactly 16 bytes: 'TOKN' + seq + total + msg_id.
        // Some senders may append extra fields after the header; treat any extra
        // bytes strictly as payload to avoid dropping data.
        *header_len = 16;
        return 0;
    } else {
        *seq_num = ((uint32_t)(unsigned char)buffer[0] << 24) |
                   ((uint32_t)(unsigned char)buffer[1] << 16) |
                   ((uint32_t)(unsigned char)buffer[2] << 8) |
                   ((uint32_t)(unsigned char)buffer[3]);
        *total_chunks = ((uint32_t)(unsigned char)buffer[4] << 24) |
                        ((uint32_t)(unsigned char)buffer[5] << 16) |
                        ((uint32_t)(unsigned char)buffer[6] << 8) |
                        ((uint32_t)(unsigned char)buffer[7]);
        *message_id = 0;
        *is_extended = 0;
        *header_len = 8;
        return 0;
    }
}

// Check if all chunks have been received
int all_chunks_received(void) {
    if (total_chunks_expected == 0) return 0;
    return received_chunks_count == total_chunks_expected;
}

// Assemble all chunks into complete text
int assemble_text(char *output, int max_size) {
    int total_length = 0;
    
    for (uint32_t i = 0; i < total_chunks_expected; i++) {
        if (!chunks[i].received) {
            return -1; // Missing chunk
        }
        
        if (total_length + chunks[i].length >= max_size) {
            return -1; // Output buffer too small
        }
        
        memcpy(output + total_length, chunks[i].data, chunks[i].length);
        total_length += chunks[i].length;
    }
    
    output[total_length] = '\0';
    return total_length;
}

// Reset chunk tracking for new message
void reset_chunks(void) {
    for (uint32_t i = 0; i <= max_chunk_received && i < MAX_CHUNKS; i++) {
        chunks[i].received = 0;
        chunks[i].length = 0;
    }
    max_chunk_received = 0;
    total_chunks_expected = 0;
    received_chunks_count = 0;
}

int main(int argc, char *argv[]) {
    int ret;
    int sockfd;
    struct sockaddr_in server_addr;
    char assembled_text[MAX_TEXT_SIZE];
    int exit_code = 0;

    
    // Determine if running in embed-mode (suppress heavy logs)
    int embed_mode = 0;
    const char* embed_env = getenv("DPDK_EMBED_MODE");
    if (embed_env && embed_env[0] == '1') embed_mode = 1;
    
    // Initialize DPDK EAL
    ret = rte_eal_init(argc, argv);
    if (ret < 0) {
        fprintf(stderr, "Error: Failed to initialize DPDK EAL: %s\n", strerror(-ret));
        return -1;
    }

    // Get TSC frequency for timing measurements
    tsc_hz = rte_get_tsc_hz();
    if (tsc_hz == 0) {
        fprintf(stderr, "Warning: Could not get TSC frequency, timing may be inaccurate\n");
        tsc_hz = 1; // Prevent division by zero
    }

    // Determine model type based on command line argument
    bpe_model_type_t model_type = BPE_MODEL_MODERNBERT;  // Default
    bool is_gpt2 = false;
    bool is_json_vocab = false;
    bool debug_output = false;
    int rx_trace = 0; // env-enabled RX tracing regardless of --debug
    
    // Check for model argument
    if (argc > 1) {
        const char *model_arg = argv[argc - 1];
        if (model_arg[0] != '-' && strstr(model_arg, "tokenizer_dpdk_bpe_vm") == NULL) {
            if (strcmp(model_arg, "diffugpt-m") == 0 || strstr(model_arg, "gpt2") != NULL) {
                model_type = BPE_MODEL_GPT2;
                is_gpt2 = true;
                is_json_vocab = true;
            }
        }
        // Detect debug flag in arguments
        for (int i = 1; i < argc; i++) {
            if (strcmp(argv[i], "--debug") == 0) { debug_output = true; break; }
        }
    }
    // Enable RX tracing via environment (works even if --debug not parsed)
    {
        const char* rxenv = getenv("DPDK_RX_TRACE");
        if (rxenv && (rxenv[0] == '1' || rxenv[0] == 'T' || rxenv[0] == 't' || rxenv[0] == 'y' || rxenv[0] == 'Y')) {
            rx_trace = 1;
        }
    
    // Optional: CPU pinning and RT scheduling for lower jitter
    const char* pin_env = getenv("DPDK_PIN_CORE");
    if (pin_env && pin_env[0] != '\0') {
        int core = atoi(pin_env);
        if (core >= 0) {
            cpu_set_t set;
            CPU_ZERO(&set);
            CPU_SET((unsigned)core, &set);
            if (pthread_setaffinity_np(pthread_self(), sizeof(set), &set) != 0) {
                fprintf(stderr, "Warning: pthread_setaffinity_np(%d) failed: %s\n", core, strerror(errno));
            }
            // Enforce isolation: refuse to run if core is not isolated
            const char* allow_env = getenv("DPDK_ALLOW_NON_ISOLATED");
            if (!is_cpu_isolated(core)) {
                if (allow_env && allow_env[0] == '1') {
                    fprintf(stderr, "Warning: CPU core %d not isolated; proceeding due to DPDK_ALLOW_NON_ISOLATED=1\n", core);
                } else {
                    fprintf(stderr, "Error: DPDK requires isolated CPU core %d. Configure isolcpus (and ideally nohz_full, rcu_nocbs) to include this core and restart.\n", core);
                    exit_code = 2;
                    goto cleanup_eal;
                }
            }
        }
    }
    const char* rt_env = getenv("DPDK_RT_PRIO");
    if (rt_env && rt_env[0] != '\0') {
        int prio = atoi(rt_env);
        if (prio > 0) {
            struct sched_param sp; memset(&sp, 0, sizeof(sp)); sp.sched_priority = prio;
            if (sched_setscheduler(0, SCHED_FIFO, &sp) != 0) {
                fprintf(stderr, "Warning: sched_setscheduler FIFO prio=%d failed: %s\n", prio, strerror(errno));
            }
        }
    }

    // Initialize BPE model
    unsigned int socket_id = rte_socket_id();
    ret = dpdk_bpe_init(socket_id, model_type);
    if (ret < 0) {
        const char* reason = dpdk_bpe_last_error();
        fprintf(stderr, "Error: Failed to initialize BPE model: %s\n", reason ? reason : "unknown");
        exit_code = 1;
        goto cleanup_eal;
    }

    // Load BPE model from extracted merge rules (optimized format)
    // Try to find the project root directory
    char merge_file_path[512];
    char vocab_file_path[512];
    const char *default_merge = "src/dpdk/tokenizer/json/modernbert_base_merges.txt";
    const char *default_vocab = "src/dpdk/tokenizer/json/modernbert-base_vocab/vocab_token_to_id.txt";
    
    // Check if we can access files from current directory
    FILE *test = fopen(default_merge, "r");
    if (test) {
        // Running from project root
        fclose(test);
        strcpy(merge_file_path, default_merge);
        strcpy(vocab_file_path, default_vocab);
    } else {
        // Try from parent directories (up to 4 levels)
        const char *prefixes[] = {"../", "../../", "../../../", "../../../../"};
        int found = 0;
        for (int i = 0; i < 4; i++) {
            snprintf(merge_file_path, sizeof(merge_file_path), "%s%s", prefixes[i], default_merge);
            test = fopen(merge_file_path, "r");
            if (test) {
                fclose(test);
                snprintf(vocab_file_path, sizeof(vocab_file_path), "%s%s", prefixes[i], default_vocab);
                found = 1;
                break;
            }
        }
        if (!found) {
            // Fallback to original paths
            strcpy(merge_file_path, default_merge);
            strcpy(vocab_file_path, default_vocab);
        }
    }
    
    const char *merge_file = merge_file_path;
    const char *vocab_file = vocab_file_path;
    
    // Look for model argument - should be the last argument after all DPDK args
    const char *tokenizer_json_path = NULL;
    char tokenizer_json_full_path[512];
    
    if (argc > 1) {
        const char *model_arg = argv[argc - 1]; // Last argument should be our model
        
        // Check if it looks like a model name (not a DPDK argument)
        if (model_arg[0] != '-' && strstr(model_arg, "tokenizer_dpdk_bpe_vm") == NULL) {
            // Map model names to merge files and vocab files
            const char *model_merge = NULL;
            const char *model_vocab = NULL;
            
            if (strcmp(model_arg, "modernbert-base") == 0 || strcmp(model_arg, "answerdotai/ModernBERT-base") == 0) {
                model_merge = "src/dpdk/tokenizer/json/modernbert_base_merges.txt";
                model_vocab = "src/dpdk/tokenizer/json/modernbert-base_vocab/vocab_token_to_id.txt";
                tokenizer_json_path = "tokenizer_data/answerdotai/ModernBERT-base/tokenizer.json";
            } else if (strcmp(model_arg, "modernbert-large") == 0 || strcmp(model_arg, "answerdotai/ModernBert-large") == 0) {
                model_merge = "src/dpdk/tokenizer/json/modernbert_large_merges.txt";
                model_vocab = "src/dpdk/tokenizer/json/modernbert-large_vocab/vocab_token_to_id.txt";
                tokenizer_json_path = "tokenizer_data/answerdotai/ModernBert-large/tokenizer.json";
            } else if (strcmp(model_arg, "diffugpt-m") == 0) {
                model_merge = "tokenizer_data/diffugpt-m/merges.txt";
                model_vocab = "tokenizer_data/diffugpt-m/vocab.json";
                // diffugpt-m doesn't have tokenizer.json, will use GPT-2 defaults
                tokenizer_json_path = "tokenizer_data/gpt2/tokenizer.json";
                is_gpt2 = true;
                is_json_vocab = true;
            }  else if (strcmp(model_arg, "gpt2") == 0) {
                model_merge = "tokenizer_data/gpt2/merges.txt";
                model_vocab = "tokenizer_data/gpt2/vocab.json";
                tokenizer_json_path = "tokenizer_data/gpt2/tokenizer.json";
                is_gpt2 = true;
                is_json_vocab = true;
            }
            
            if (model_merge && model_vocab) {
                // Apply the same path resolution logic
                FILE *test = fopen(model_merge, "r");
                if (test) {
                    fclose(test);
                    strcpy(merge_file_path, model_merge);
                    strcpy(vocab_file_path, model_vocab);
                } else {
                    // Try from parent directories
                    const char *prefixes[] = {"../", "../../", "../../../", "../../../../"};
                    for (int i = 0; i < 4; i++) {
                        snprintf(merge_file_path, sizeof(merge_file_path), "%s%s", prefixes[i], model_merge);
                        test = fopen(merge_file_path, "r");
                        if (test) {
                            fclose(test);
                            snprintf(vocab_file_path, sizeof(vocab_file_path), "%s%s", prefixes[i], model_vocab);
                            break;
                        }
                    }
                }
                merge_file = merge_file_path;
                vocab_file = vocab_file_path;
            } else {
                // Assume it's a direct file path to merge file
                merge_file = model_arg;
            }
        }
    }
    
    int merges_loaded = dpdk_bpe_load_merges_from_file(merge_file, is_gpt2);
    if (merges_loaded < 0) {
        printf("Warning: Could not load BPE merges from %s, using basic tokenization\n", merge_file);
    } else {
        printf("Loaded %d BPE merge rules from %s\n", merges_loaded, merge_file);
    }

    // Load vocabulary for O(1) token→ID lookup
    int vocab_loaded = dpdk_bpe_load_vocab_from_file(vocab_file, is_json_vocab);
    if (vocab_loaded < 0) {
        printf("Warning: Could not load vocabulary from %s, token IDs will not be available\n", vocab_file);
    } else {
        printf("Loaded %d vocabulary tokens from %s\n", vocab_loaded, vocab_file);
    }
    
    // Load tokenizer configuration if available (for GPT-2 models)
    if (is_gpt2 && tokenizer_json_path) {
        // Try to find the tokenizer.json file
        FILE *test = fopen(tokenizer_json_path, "r");
        if (test) {
            fclose(test);
            strcpy(tokenizer_json_full_path, tokenizer_json_path);
        } else {
            // Try from parent directories
            const char *prefixes[] = {"../", "../../", "../../../", "../../../../"};
            int found = 0;
            for (int i = 0; i < 4; i++) {
                snprintf(tokenizer_json_full_path, sizeof(tokenizer_json_full_path), 
                         "%s%s", prefixes[i], tokenizer_json_path);
                test = fopen(tokenizer_json_full_path, "r");
                if (test) {
                    fclose(test);
                    found = 1;
                    break;
                }
            }
            if (!found) {
                strcpy(tokenizer_json_full_path, tokenizer_json_path);
            }
        }
        
        if (dpdk_bpe_load_tokenizer_config(tokenizer_json_full_path) == 0) {
            printf("Loaded tokenizer configuration from %s\n", tokenizer_json_full_path);
        } else {
            printf("Warning: Could not load tokenizer config from %s, using defaults\n", tokenizer_json_full_path);
        }
    }

    // Initialize shared memory for token ID export (zero-copy to Python)
    if (shm_init(MAX_TOKENS) != 0) {
        fprintf(stderr, "Error: Failed to initialize shared memory for token IDs\n");
        exit_code = 1;
        goto cleanup_bpe;
    }

    // Create UDP socket
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("Error creating socket");
        exit_code = 2;
        goto cleanup_bpe;
    }

    // Increase receive buffer to tolerate bursts
    int rcvbuf = 4 * 1024 * 1024; // 4MB
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf)) < 0) {
        perror("Warning: setsockopt SO_RCVBUF failed");
    }

    // Bind socket
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(LISTEN_PORT);

    if (bind(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("Error binding socket");
        exit_code = 3;
        goto cleanup_socket;
    }

    printf("DPDK BPE Tokenizer VM listening on port %d\n", LISTEN_PORT);
    fflush(stdout);
    printf("BPE Model initialized with %d merge rules\n", dpdk_bpe_get_merge_count());
    // Avoid building token strings unless debug is enabled (faster)
    dpdk_bpe_set_produce_strings(debug_output);

    // Main processing loop using recvfrom (robust in VM/userland)
    while (1) {
        char buf[BUFFER_SIZE];
        struct sockaddr_in src; socklen_t slen = sizeof(src);
        ssize_t received = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*)&src, &slen);
        if (received < 0) {
            if (errno == EINTR) continue;
            if (debug_output || rx_trace) perror("recvfrom");
            continue;
        }
        if (debug_output || rx_trace) {
            unsigned char *b = (unsigned char*)buf;
            int dump = received < 16 ? (int)received : 16;
            unsigned short port = ntohs(src.sin_port);
            printf("RX bytes=%zd from %u.%u.%u.%u:%u first[%d]=",
                   received,
                   (src.sin_addr.s_addr) & 0xFF,
                   (src.sin_addr.s_addr >> 8) & 0xFF,
                   (src.sin_addr.s_addr >> 16) & 0xFF,
                   (src.sin_addr.s_addr >> 24) & 0xFF,
                   port, dump);
            for (int i = 0; i < dump; i++) printf("%s%02X", (i?" ":""), b[i]);
            printf("\n");
            fflush(stdout);
        }
        if (received < 8) { if (debug_output || rx_trace) { printf("RX drop: too small (%zd)\n", received); fflush(stdout);} continue; }
        char* bufp = (char*)buf;
        uint64_t packet_arrival_time = rte_rdtsc();

        uint32_t seq_num, total_chunks, msg_id; int is_ext = 0; int hdr_len = 0;
        if (parse_chunk_header(bufp, received, &seq_num, &total_chunks, &msg_id, &is_ext, &hdr_len) != 0) {
            if (debug_output || rx_trace) { printf("RX drop: header parse failed (bytes=%zd)\n", received); fflush(stdout);} 
            continue; }
        if (debug_output || rx_trace) {
            printf("RX chunk: is_ext=%d seq=%u total=%u msg_id=%u payload=%zd\n", is_ext, seq_num, total_chunks, msg_id, received - hdr_len);
            fflush(stdout);
        }
        if (seq_num >= MAX_CHUNKS || total_chunks > MAX_CHUNKS || total_chunks == 0) {
            if (debug_output || rx_trace) { printf("RX drop: invalid header values (seq=%u total=%u)\n", seq_num, total_chunks); fflush(stdout);} 
            continue; }

            // Only start a new message when we see the first chunk (seq==0).
            // This avoids dropping an in-flight message if a later packet for the next
            // message arrives before the last chunk of the current one.
        if (!is_ext) {
            if (total_chunks_expected == 0) {
                total_chunks_expected = total_chunks;
            }
            if (seq_num == 0 && received_chunks_count > 0) {
                reset_chunks();
                total_chunks_expected = total_chunks;
            }
        }

        if (!is_ext) {
            int data_length = (int)received - hdr_len;
            if (data_length > 0 && data_length <= 1200) {
                if (!chunks[seq_num].received) {
                    memcpy(chunks[seq_num].data, bufp + hdr_len, (size_t)data_length);
                    chunks[seq_num].length = data_length;
                    chunks[seq_num].received = 1;
                    received_chunks_count++;
                    if (seq_num > max_chunk_received) max_chunk_received = seq_num;
                    if (debug_output || rx_trace) { printf("RX store legacy: seq=%u len=%d count=%u/%u\n", seq_num, data_length, received_chunks_count, total_chunks_expected ? total_chunks_expected : total_chunks); fflush(stdout);}                        
                }
            }
        } else {
            struct message_ctx* m = get_or_alloc_ctx(msg_id, total_chunks);
            if (m->received_chunks_count == 0) m->first_arrival_tsc = packet_arrival_time;
            int data_length = (int)received - hdr_len;
            if (data_length > 0 && data_length <= 1200) {
                if (!m->chunks[seq_num].received) {
                    memcpy(m->chunks[seq_num].data, bufp + hdr_len, (size_t)data_length);
                    m->chunks[seq_num].length = data_length;
                    m->chunks[seq_num].received = 1;
                    m->received_chunks_count++;
                    if (seq_num > m->max_chunk_received) m->max_chunk_received = seq_num;
                    if (debug_output || rx_trace) { printf("RX store ext: msg=%u seq=%u len=%d count=%u/%u\n", msg_id, seq_num, data_length, m->received_chunks_count, m->total_chunks_expected ? m->total_chunks_expected : total_chunks); fflush(stdout);}                        
                }
            }
            if (m->total_chunks_expected == 0) m->total_chunks_expected = total_chunks;
        }

        int ready = (!is_ext ? all_chunks_received() : (get_or_alloc_ctx(msg_id, total_chunks)->received_chunks_count == total_chunks));
        if (debug_output || rx_trace) {
            if (!is_ext) {
                printf("RX status: received_chunks=%u/%u ready=%d\n", received_chunks_count, total_chunks_expected, ready);
            } else {
                struct message_ctx* dm = get_or_alloc_ctx(msg_id, total_chunks);
                printf("RX status: msg %u chunks=%u/%u ready=%d\n", msg_id, dm->received_chunks_count, dm->total_chunks_expected, ready);
            }
            fflush(stdout);
        }
        if (ready) {
            if (debug_output || rx_trace) { printf("RX ready: assembling text (is_ext=%d)\n", is_ext); fflush(stdout);}            
            uint64_t assembly_start_time = rte_rdtsc();
            
            // Assemble complete text
            int text_length;
            if (!is_ext) {
                text_length = assemble_text(assembled_text, MAX_TEXT_SIZE - 1);
                if (text_length < 0) { reset_chunks(); continue; }
            } else {
                struct message_ctx* m = get_or_alloc_ctx(msg_id, total_chunks);
                int total_length = 0; int ok = 1;
                for (uint32_t i = 0; i < m->total_chunks_expected; i++) {
                    if (!m->chunks[i].received) { ok = 0; break; }
                    if (total_length + m->chunks[i].length >= (MAX_TEXT_SIZE - 1)) { ok = 0; break; }
                    memcpy(assembled_text + total_length, m->chunks[i].data, m->chunks[i].length);
                    total_length += m->chunks[i].length;
                }
                if (!ok) { reset_message_ctx(m); continue; }
                assembled_text[total_length] = '\0';
                text_length = total_length;
            }
            
            // Perform BPE tokenization with token IDs
            // Allocate large token string buffer on the heap to avoid stack overflow
            char (*tokens)[MAX_TOKEN_LEN] = (char (*)[MAX_TOKEN_LEN])rte_zmalloc_socket(
                "dpdk_out_tokens", (size_t)MAX_TOKENS * (size_t)MAX_TOKEN_LEN,
                RTE_CACHE_LINE_SIZE, rte_socket_id());
            int token_ids[MAX_TOKENS];
            if (!tokens) {
                fprintf(stderr, "Error: Failed to allocate output tokens buffer\n");
                if (!is_ext) { reset_chunks(); } else { struct message_ctx* m = get_or_alloc_ctx(msg_id, total_chunks); reset_message_ctx(m); }
                continue;
            }

            uint64_t tokenize_start_time = rte_rdtsc();            
            int num_tokens = dpdk_bpe_tokenize_with_ids(assembled_text, tokens, token_ids, MAX_TOKENS);
            uint64_t tokenize_end_time = rte_rdtsc();

            if (num_tokens < 0) {
                rte_free(tokens);
                reset_chunks();
                continue;
            }

            // Publish token IDs to shared memory for zero-copy consumption
            if (!is_ext) {
                shm_publish_tokens(token_ids, num_tokens, 0, packet_arrival_time,
                                   assembly_start_time, tokenize_start_time, tokenize_end_time);
            } else {
                // For extended messages, use first arrival timestamp for packet_arrival_time
                struct message_ctx* m2 = get_or_alloc_ctx(msg_id, total_chunks);
                uint64_t first = m2->first_arrival_tsc ? m2->first_arrival_tsc : packet_arrival_time;
                shm_publish_tokens(token_ids, num_tokens, msg_id, first,
                                   assembly_start_time, tokenize_start_time, tokenize_end_time);
            }

            // Output results in structured format for monitoring
            printf("DPDK_TOKENIZATION_START\n");
            if (debug_output) {
                printf("ORIGINAL_TEXT: %s\n", assembled_text);
                printf("NUM_CHUNKS: %d\n", total_chunks_expected);
                printf("TEXT_LENGTH: %d\n", text_length);
                printf("NUM_TOKENS: %d\n", num_tokens);
            }
            
            // Print tokens (debug only; suppress in embed-mode to avoid huge lines)
            if (debug_output && !embed_mode) {
                printf("TOKENS: ");
                for (int i = 0; i < num_tokens; i++) {
                    printf("%s", tokens[i]);
                    if (i < num_tokens - 1) printf(" ");
                }
                printf("\n");
            }
            
            // Print token IDs (debug only; suppress in embed-mode to avoid huge lines)
            if (debug_output && !embed_mode) {
                printf("TOKEN_IDS: ");
                for (int i = 0; i < num_tokens; i++) {
                    printf("%d", token_ids[i]);
                    if (i < num_tokens - 1) printf(" ");
                }
                printf("\n");
            }
            
            // Performance timing (suppress in embed-mode to avoid overhead)
            if (!embed_mode) {
                if (!is_ext) {
                    printf("PACKET_ARRIVAL_TIME: %lu\n", packet_arrival_time);
                } else {
                    struct message_ctx* m2 = get_or_alloc_ctx(msg_id, total_chunks);
                    uint64_t first = m2->first_arrival_tsc ? m2->first_arrival_tsc : packet_arrival_time;
                    printf("PACKET_ARRIVAL_TIME: %lu\n", first);
                }
                printf("ASSEMBLY_START_TIME: %lu\n", assembly_start_time);
                printf("TOKENIZE_START_TIME: %lu\n", tokenize_start_time);
                printf("TOKENIZE_END_TIME: %lu\n", tokenize_end_time);
                printf("TSC_FREQUENCY: %lu\n", tsc_hz);
                // Cache counters (delta per message to minimize I/O)
                {
                    uint64_t cL=0, cH=0, cI=0, cF=0, cSL=0, cSO=0;
                    if (dpdk_bpe_get_cache_stats_ext(&cL, &cH, &cI, &cF, &cSL, &cSO) == 0) {
                        uint64_t dL = (cL >= prev_cache_lookups) ? (cL - prev_cache_lookups) : 0;
                        uint64_t dH = (cH >= prev_cache_hits) ? (cH - prev_cache_hits) : 0;
                        uint64_t dI = (cI >= prev_cache_inserts) ? (cI - prev_cache_inserts) : 0;
                        uint64_t dF = (cF >= prev_cache_insert_fails) ? (cF - prev_cache_insert_fails) : 0;
                        uint64_t dSL = (cSL >= prev_cache_skip_longkey) ? (cSL - prev_cache_skip_longkey) : 0;
                        uint64_t dSO = (cSO >= prev_cache_skip_oversize) ? (cSO - prev_cache_skip_oversize) : 0;
                        printf("CACHE_LOOKUPS: %lu\n", dL);
                        printf("CACHE_HITS: %lu\n", dH);
                        printf("CACHE_INSERTS: %lu\n", dI);
                        printf("CACHE_INSERT_FAILS: %lu\n", dF);
                        printf("CACHE_SKIP_LONGKEY: %lu\n", dSL);
                        printf("CACHE_SKIP_OVERSIZE: %lu\n", dSO);
                        prev_cache_lookups = cL;
                        prev_cache_hits = cH;
                        prev_cache_inserts = cI;
                        prev_cache_insert_fails = cF;
                        prev_cache_skip_longkey = cSL;
                        prev_cache_skip_oversize = cSO;
                    }
                }
            }
            
            // BPE model statistics
            if (debug_output) {
                struct bpe_stats stats;
                if (dpdk_bpe_get_stats(&stats) == 0) {
                    printf("BPE_VOCAB_SIZE: %d\n", stats.vocab_size);
                    printf("BPE_MERGE_COUNT: %d\n", stats.merge_count);
                    printf("BPE_POOL_SIZE: %d\n", stats.token_pool_size);
                    printf("BPE_POOL_FREE: %d\n", stats.token_pool_free);
                }
            }
            
            printf("DPDK_TOKENIZATION_END\n");
            fflush(stdout);

            // Reset for next message
            if (!is_ext) {
                reset_chunks();
            } else {
                struct message_ctx* m3 = get_or_alloc_ctx(msg_id, total_chunks);
                reset_message_ctx(m3);
            }
            // Free heap buffer
            rte_free(tokens);
            }
        }
    }

cleanup_socket:
    close(sockfd);
cleanup_bpe:
    dpdk_bpe_cleanup();
cleanup_eal:
    shm_cleanup();
    rte_eal_cleanup();
    return exit_code;
}
