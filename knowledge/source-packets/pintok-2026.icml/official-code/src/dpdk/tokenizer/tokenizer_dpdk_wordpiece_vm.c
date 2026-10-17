// tokenizer_dpdk_wordpiece_vm.c - DPDK-based WordPiece tokenizer optimized for VM environments
#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sched.h>
#include <pthread.h>
#include <errno.h>
#include <ctype.h>
#include <rte_eal.h>
#include <rte_mbuf.h>
#include <rte_mempool.h>
#include <rte_cycles.h>
#include "wordpiece_util.h"

#define LISTEN_PORT    6000
#define NUM_MBUFS      8191
#define MBUF_CACHE_SIZE 250
#define MAX_CHUNKS     1000
#define MAX_TEXT_SIZE  (MAX_CHUNKS * 1200)
#define BUFFER_SIZE    2048

// Default relative vocabulary path for WordPiece; can be overridden with
// environment variable DPDK_WORDPIECE_VOCAB.
#define DEFAULT_WP_VOCAB_JSON "src/dpdk/tokenizer/json/simple.json"

// Structure to store received chunks
struct chunk_data {
    char data[1200];
    int length;
    int received;
};

static struct chunk_data chunks[MAX_CHUNKS];
static int max_chunk_received = -1;
static int total_chunks_expected = 0;
static uint64_t tsc_hz = 0;

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
    FILE* f = fopen("/sys/devices/system/cpu/isolated", "r");
    if (f) {
        char line[256] = {0};
        size_t n = fread(line, 1, sizeof(line)-1, f);
        fclose(f);
        if (n > 0) {
            if (parse_cpu_list_has(line, cpu)) return 1;
        }
    }
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
                char cleaned[512] = {0}; size_t ci = 0;
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

// Function to extract sequence number and total chunks from packet
void extract_chunk_header(const char *buffer, uint32_t *seq_num, uint32_t *total_chunks) {
    *seq_num = ((uint32_t)(unsigned char)buffer[0] << 24) |
               ((uint32_t)(unsigned char)buffer[1] << 16) |
               ((uint32_t)(unsigned char)buffer[2] << 8) |
               ((uint32_t)(unsigned char)buffer[3]);
               
    *total_chunks = ((uint32_t)(unsigned char)buffer[4] << 24) |
                    ((uint32_t)(unsigned char)buffer[5] << 16) |
                    ((uint32_t)(unsigned char)buffer[6] << 8) |
                    ((uint32_t)(unsigned char)buffer[7]);
}

// Check if all chunks have been received
int all_chunks_received(void) {
    if (total_chunks_expected == 0) return 0;
    
    for (int i = 0; i < total_chunks_expected; i++) {
        if (!chunks[i].received) {
            return 0;
        }
    }
    return 1;
}

// Process complete message when all chunks are received
void process_complete_message(uint64_t first_packet_arrival) {
    // Concatenate all chunks
    char complete_text[MAX_TEXT_SIZE] = {0};
    int total_length = 0;
    
    for (int i = 0; i < total_chunks_expected && total_length < MAX_TEXT_SIZE - 1; i++) {
        if (chunks[i].received) {
            int copy_len = chunks[i].length;
            if (total_length + copy_len >= MAX_TEXT_SIZE) {
                copy_len = MAX_TEXT_SIZE - total_length - 1;
            }
            memcpy(complete_text + total_length, chunks[i].data, copy_len);
            total_length += copy_len;
        }
    }
    complete_text[total_length] = '\0';
    
    // Tokenize using WordPiece tokenizer
    char tokens[MAX_TOKENS][MAX_TOKEN_LEN];
    int num_tokens = dpdk_wordpiece_tokenize(complete_text, tokens, MAX_TOKENS);
    
    uint64_t tokenize_cycles = rte_rdtsc();
    
    // Output results
    printf("DPDK_TOKENIZATION_START\n");
    printf("PACKET_ARRIVAL_TIME: %lu\n", first_packet_arrival);
    printf("TOKENIZE_END_TIME: %lu\n", tokenize_cycles);
    printf("TSC_FREQUENCY: %lu\n", tsc_hz);
    printf("ORIGINAL_TEXT: %s\n", complete_text);
    printf("NUM_TOKENS: %d\n", num_tokens);
    printf("TOKENS: ");
    for (int i = 0; i < num_tokens; i++) {
        printf("%s", tokens[i]);
        if (i < num_tokens - 1) printf(" ");
    }
    printf("\n");
    printf("TOKEN_IDS: ");
    for (int i = 0; i < num_tokens; i++) {
        int token_id = dpdk_wordpiece_get_id_by_token(tokens[i]);
        printf("%d", token_id);
        if (i < num_tokens - 1) printf(" ");
    }
    printf("\n");
    printf("DPDK_TOKENIZATION_END\n");
    fflush(stdout);
    
    double total_latency_us = (double)(tokenize_cycles - first_packet_arrival) * 1000000.0 / tsc_hz;
    fprintf(stderr, "DPDK_WORDPIECE_LATENCY: %.2f us (complete message)\n", total_latency_us);
    
    // Reset for next message
    memset(chunks, 0, sizeof(chunks));
    max_chunk_received = -1;
    total_chunks_expected = 0;
}

int main(int argc, char **argv)
{
    // Initialize DPDK EAL with minimal configuration for VM environments
    int ret = rte_eal_init(argc, argv);
    if (ret < 0) {
        fprintf(stderr, "Failed to initialize DPDK EAL, falling back to socket mode\n");
        // Fall back to regular socket implementation
        goto socket_mode;
    }

    // Initialize TSC frequency
    tsc_hz = rte_get_tsc_hz();
    fprintf(stderr, "DPDK WordPiece VM Tokenizer initialized\n");
    fprintf(stderr, "TSC frequency: %lu Hz\n", tsc_hz);

    // Optional: CPU pinning and RT scheduling (match BPE VM behavior)
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
            const char* allow_env = getenv("DPDK_ALLOW_NON_ISOLATED");
            if (!is_cpu_isolated(core)) {
                if (allow_env && allow_env[0] == '1') {
                    fprintf(stderr, "Warning: CPU core %d not isolated; proceeding due to DPDK_ALLOW_NON_ISOLATED=1\n", core);
                } else {
                    fprintf(stderr, "Error: DPDK requires isolated CPU core %d. Configure isolcpus (and ideally nohz_full, rcu_nocbs) to include this core and restart.\n", core);
                    goto socket_mode;
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

    // Initialize WordPiece model
    if (dpdk_wordpiece_init(rte_socket_id()) < 0) {
        fprintf(stderr, "Failed to initialize WordPiece model\n");
        goto socket_mode;
    }

    // Load default vocabulary with repo-relative fallback and env override
    const char* vocab_file = getenv("DPDK_WORDPIECE_VOCAB");
    char vocab_resolved[512];
    if (!vocab_file || vocab_file[0] == '\0') {
        vocab_file = DEFAULT_WP_VOCAB_JSON;
    }
    FILE *vf = fopen(vocab_file, "r");
    if (!vf) {
        const char *prefixes[] = {"../", "../../", "../../../", "../../../../"};
        for (size_t i = 0; i < sizeof(prefixes)/sizeof(prefixes[0]); ++i) {
            snprintf(vocab_resolved, sizeof(vocab_resolved), "%s%s", prefixes[i], vocab_file);
            vf = fopen(vocab_resolved, "r");
            if (vf) { vocab_file = vocab_resolved; break; }
        }
    }
    if (vf) fclose(vf);
    int vocab_size = dpdk_wordpiece_load_vocab_from_file(vocab_file);
    if (vocab_size < 0) {
        fprintf(stderr, "Warning: Could not load vocabulary from %s, using basic tokens\n", vocab_file);
        // Add some basic tokens
        dpdk_wordpiece_add_token("[UNK]");
        dpdk_wordpiece_add_token("[CLS]");
        dpdk_wordpiece_add_token("[SEP]");
        dpdk_wordpiece_add_token("[PAD]");
        dpdk_wordpiece_add_token("[MASK]");
    } else {
        fprintf(stderr, "Loaded %d tokens from vocabulary\n", vocab_size);
    }

    // Create mbuf pool for memory management (even without network ports)
    struct rte_mempool *mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", NUM_MBUFS,
        MBUF_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE, rte_socket_id());
    if (mbuf_pool == NULL) {
        fprintf(stderr, "Cannot create mbuf pool, falling back to socket mode\n");
        goto socket_mode;
    }

    fprintf(stderr, "DPDK memory pool created successfully\n");
    fprintf(stderr, "Using socket-based packet reception with DPDK WordPiece timing\n");

socket_mode:
    {
    // Use regular UDP socket for packet reception
    int sockfd;
    struct sockaddr_in servaddr, cliaddr;
    socklen_t len = sizeof(cliaddr);
    char buffer[BUFFER_SIZE];

    // Create socket
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }

    memset(&servaddr, 0, sizeof(servaddr));
    memset(&cliaddr, 0, sizeof(cliaddr));

    // Server information
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY;
    servaddr.sin_port = htons(LISTEN_PORT);

    // Bind socket
    if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    fprintf(stderr, "DPDK WordPiece VM tokenizer listening on UDP port %d\n", LISTEN_PORT);
    fprintf(stderr, "Using DPDK TSC timing with WordPiece tokenization\n");

    // Main packet processing loop
    while (1) {
        int n = recvfrom(sockfd, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&cliaddr, &len);
        if (n > 0) {
            uint64_t packet_arrival_cycles = rte_rdtsc();
            
            // Process payload with 8-byte header format
            if (n >= 8) {
                uint32_t seq_num, total_chunks;
                extract_chunk_header(buffer, &seq_num, &total_chunks);
                
                int text_payload_len = n - 8;
                
                fprintf(stderr, "Received chunk %u/%u, payload length: %d\n", 
                       seq_num, total_chunks, text_payload_len);
                
                if (seq_num < MAX_CHUNKS && text_payload_len > 0) {
                    memcpy(chunks[seq_num].data, buffer + 8, text_payload_len);
                    chunks[seq_num].length = text_payload_len;
                    chunks[seq_num].received = 1;
                    
                    if (total_chunks_expected == 0 || (int)total_chunks > total_chunks_expected) {
                        total_chunks_expected = total_chunks;
                    }
                    
                    if ((int)seq_num > max_chunk_received) {
                        max_chunk_received = seq_num;
                    }
                    
                    // Check if we have all chunks
                    if (all_chunks_received()) {
                        process_complete_message(packet_arrival_cycles);
                    }
                }
            } else {
                // Handle as plain text for backward compatibility
                buffer[n] = '\0';
                
                fprintf(stderr, "Received plain text: %s\n", buffer);
                
                // Tokenize using WordPiece tokenizer
                char tokens[MAX_TOKENS][MAX_TOKEN_LEN];
                int num_tokens = dpdk_wordpiece_tokenize(buffer, tokens, MAX_TOKENS);
                
                uint64_t tokenize_cycles = rte_rdtsc();
                
                // Output results
                printf("DPDK_TOKENIZATION_START\n");
                printf("PACKET_ARRIVAL_TIME: %lu\n", packet_arrival_cycles);
                printf("TOKENIZE_END_TIME: %lu\n", tokenize_cycles);
                printf("TSC_FREQUENCY: %lu\n", tsc_hz);
                printf("ORIGINAL_TEXT: %s\n", buffer);
                printf("NUM_TOKENS: %d\n", num_tokens);
                printf("TOKENS: ");
                for (int i = 0; i < num_tokens; i++) {
                    printf("%s", tokens[i]);
                    if (i < num_tokens - 1) printf(" ");
                }
                printf("\n");
                printf("TOKEN_IDS: ");
                for (int i = 0; i < num_tokens; i++) {
                    int token_id = dpdk_wordpiece_get_id_by_token(tokens[i]);
                    printf("%d", token_id);
                    if (i < num_tokens - 1) printf(" ");
                }
                printf("\n");
                printf("DPDK_TOKENIZATION_END\n");
                fflush(stdout);
                
                double total_latency_us = (double)(tokenize_cycles - packet_arrival_cycles) * 1000000.0 / tsc_hz;
                fprintf(stderr, "DPDK_WORDPIECE_LATENCY: %.2f us\n", total_latency_us);
            }
        }
    }

    close(sockfd);
    }
    return EXIT_SUCCESS;
}
