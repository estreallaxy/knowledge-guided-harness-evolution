// Main BPE for DPDK. 
// TODO: need to clean up later for readability

#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdarg.h>
#include <rte_common.h>
#include <rte_memory.h>
#include <rte_mempool.h>
#include <rte_mbuf.h>
#include <rte_log.h>
#include <rte_malloc.h>
#include <rte_hash.h>
#include <rte_jhash.h>
#include "bpe_util.h"
#include "vocab_util.h"

#define BPE_MEMPOOL_SIZE 16384
#define BPE_CACHE_SIZE 256
#define BPE_TOKEN_CACHE_DEFAULT_CAPACITY 100000
#define BPE_TOKEN_CACHE_MAX_INPUT_LEN    256
#define BPE_TOKEN_CACHE_ENTRY_DATA       512

// GPT-2 continuation-space prefix (U+0120 'Ġ') used by byte-level BPE tokenizers
#define GPT2_CONT_PREFIX "\xC4\xA0"
#define GPT2_CONT_PREFIX_LEN 2

// Default relative path to a GPT-2 style tokenizer.json; can be overridden via
// environment variable DPDK_BPE_TOKENIZER_JSON.
#define DEFAULT_GPT2_TOKENIZER_JSON "tokenizer_data/gpt2/tokenizer.json"

// DPDK logging
#define RTE_LOGTYPE_BPE RTE_LOGTYPE_USER1

typedef struct {
    uint32_t ha;
    uint32_t hb;
} merge_key_t;

static inline uint32_t bpe_token_hash_len(const char* s, int len) {
    if (!s || len <= 0) return 0;
    return rte_jhash(s, (uint32_t)len, 0x12345678);
}

static inline uint32_t bpe_token_hash(const char* s) {
    if (!s) return 0;
    size_t n = strnlen(s, MAX_TOKEN_LEN);
    return bpe_token_hash_len(s, (int)n);
}

typedef struct {
    char first[MAX_TOKEN_LEN];
    char second[MAX_TOKEN_LEN];
    int priority;
} __rte_cache_aligned bpe_merge_t;

typedef struct {
    bpe_merge_t *merges;
    int num_merges;
    char (*vocab)[MAX_TOKEN_LEN];
    int vocab_size;
    struct rte_mempool *token_pool;
    struct rte_mempool *merge_pool;
    struct rte_hash *merge_hash;  // Hash table for merge lookups. Keeping this for now since it speeds up.
    struct rte_hash *id_merge_hash; // (ID,ID) -> (rank,new_id)
    struct {
        int rank;
        uint32_t new_id;
    } *id_merge_vals;
    int num_id_merges;
    bpe_model_type_t model_type;
    uint32_t bytes_to_unicode[256];  // Maps byte values to unicode codepoints
    uint8_t unicode_to_bytes[512];   // Inverse mapping
    bool bytes_to_unicode_initialized;
    // ByteLevel config (TODO: are these all necessary?)
    bool bl_pre_add_prefix_space;
    bool bl_pre_trim_offsets;
    bool bl_post_add_prefix_space;
    bool bl_post_trim_offsets;
    bool bl_dec_add_prefix_space;
    bool bl_dec_trim_offsets;
    // Token cache for pre-token -> merged subword sequence
    struct rte_hash *token_cache_hash;
    struct rte_mempool *token_cache_pool;
    uint32_t token_cache_capacity;
    bool token_cache_enabled;
    // Cache counters (since model init): Only for debugging / paper.
    uint64_t cache_lookups;
    uint64_t cache_hits;
    uint64_t cache_inserts;
    uint64_t cache_insert_fails;
    uint64_t cache_skip_longkey;
    uint64_t cache_skip_oversize;
    // Output control
    bool produce_strings;
} __rte_cache_aligned bpe_model_t;

// Global BPE model instance
static bpe_model_t *bpe_model = NULL;
static char bpe_last_error[256] = {0};

// Error handling
static void bpe_set_error(const char* fmt, ...) {
    if (!fmt) { bpe_last_error[0] = '\0'; return; }
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(bpe_last_error, sizeof(bpe_last_error), fmt, ap);
    va_end(ap);
}

const char* dpdk_bpe_last_error(void) {
    if (bpe_last_error[0] == '\0') return "no error";
    return bpe_last_error;
}

static void bl_set_gpt2_defaults(void);

// Token cache (per pre-token)
typedef struct {
    uint32_t h1;
    uint32_t h2;
    uint32_t len;
} token_cache_key_t;

typedef struct {
    uint16_t count;
    uint16_t reserved;
    char data[BPE_TOKEN_CACHE_ENTRY_DATA]; // raw bytes for uint32_t ids (count * 4)
} token_cache_entry_t;

// LRU node for pre-token cache: stores key + entry pointer
static inline void token_cache_make_key(const char* s, int len, token_cache_key_t* k) {
    k->len = (uint32_t)len;
    k->h1 = rte_jhash(s, (uint32_t)len, 0x12345678u);
    k->h2 = rte_jhash(s, (uint32_t)len, 0x9e3779b9u);
}

/**
 * Initialize bytes to unicode mapping for GPT-2
 */
static int init_bytes_to_unicode(void) {
    if (!bpe_model) {
        return -1;
    }
    // Clear the mappings
    memset(bpe_model->bytes_to_unicode, 0, sizeof(bpe_model->bytes_to_unicode));
    memset(bpe_model->unicode_to_bytes, 0, sizeof(bpe_model->unicode_to_bytes));
    
    // Build the base set of bytes that map to themselves
    // This includes printable ASCII and some Latin-1 characters
    uint8_t bs[256];
    uint32_t cs[256];
    int bs_count = 0;
    
    // Range 1: '!' to '~' (33 to 126)
    for (int i = 33; i <= 126; i++) {
        bs[bs_count] = i;
        cs[bs_count] = i;
        bs_count++;
    }
    
    // Range 2: '¡' to '¬' (161 to 172)
    for (int i = 161; i <= 172; i++) {
        bs[bs_count] = i;
        cs[bs_count] = i;
        bs_count++;
    }
    
    // Range 3: '®' to 'ÿ' (174 to 255)
    for (int i = 174; i <= 255; i++) {
        bs[bs_count] = i;
        cs[bs_count] = i;
        bs_count++;
    }
    
    // Now add the remaining bytes (0-255) that aren't in bs
    // Map them to unicode codepoints starting at 256
    int n = 0;
    for (int b = 0; b < 256; b++) {
        // Check if b is already in bs
        bool found = false;
        for (int i = 0; i < bs_count; i++) {
            if (bs[i] == b) {
                found = true;
                break;
            }
        }
        
        // If not found, add it with a shifted unicode value
        if (!found) {
            bs[bs_count] = b;
            cs[bs_count] = 256 + n;  // Map to unicode codepoints 256, 257, 258...
            bs_count++;
            n++;
        }
    }
    
    // Now create the actual mappings
    for (int i = 0; i < bs_count; i++) {
        uint8_t byte_val = bs[i];
        uint32_t unicode_val = cs[i];
        
        // Store forward mapping (byte -> unicode)
        bpe_model->bytes_to_unicode[byte_val] = unicode_val;
        
        // Store inverse mapping (unicode -> byte) if within range
        if (unicode_val < 512) {
            bpe_model->unicode_to_bytes[unicode_val] = byte_val;
        }
    }
    
    bpe_model->bytes_to_unicode_initialized = true;
    
    RTE_LOG(DEBUG, BPE, "Initialized GPT-2 bytes_to_unicode mapping\n");
    RTE_LOG(DEBUG, BPE, "  Space (32) => U+%04X\n", bpe_model->bytes_to_unicode[32]);
    RTE_LOG(DEBUG, BPE, "  Tab (9)    => U+%04X\n", bpe_model->bytes_to_unicode[9]);
    RTE_LOG(DEBUG, BPE, "  Newline(10)=> U+%04X\n", bpe_model->bytes_to_unicode[10]);
    
    return 0;
}

/**
 * Convert a byte value to its unicode character representation for GPT-2
 * Returns the number of UTF-8 bytes written to output
 */
static int byte_to_unicode_char(uint8_t byte_val, char* output, int max_len) {
    if (!bpe_model || !bpe_model->bytes_to_unicode_initialized || !output || max_len < 5) {
        return -1;
    }
    
    uint32_t unicode_val = bpe_model->bytes_to_unicode[byte_val];
    
    // Convert unicode codepoint to UTF-8
    if (unicode_val < 0x80) {
        // 1-byte UTF-8
        if (max_len < 1) return -1;
        output[0] = (char)unicode_val;
        return 1;
    } else if (unicode_val < 0x800) {
        // 2-byte UTF-8
        if (max_len < 2) return -1;
        output[0] = (char)(0xC0 | (unicode_val >> 6));
        output[1] = (char)(0x80 | (unicode_val & 0x3F));
        return 2;
    } else if (unicode_val < 0x10000) {
        // 3-byte UTF-8
        if (max_len < 3) return -1;
        output[0] = (char)(0xE0 | (unicode_val >> 12));
        output[1] = (char)(0x80 | ((unicode_val >> 6) & 0x3F));
        output[2] = (char)(0x80 | (unicode_val & 0x3F));
        return 3;
    } else {
        // 4-byte UTF-8
        if (max_len < 4) return -1;
        output[0] = (char)(0xF0 | (unicode_val >> 18));
        output[1] = (char)(0x80 | ((unicode_val >> 12) & 0x3F));
        output[2] = (char)(0x80 | ((unicode_val >> 6) & 0x3F));
        output[3] = (char)(0x80 | (unicode_val & 0x3F));
        return 4;
    }
}

/**
 * Convert a string of bytes to unicode representation for GPT-2
 * This is used to encode raw text bytes before BPE processing
 */
static int bytes_to_unicode_string(const uint8_t* bytes, int byte_len, char* output, int max_len) {
    if (!bytes || !output || max_len <= 0) {
        return -1;
    }
    
    int out_pos = 0;
    for (int i = 0; i < byte_len && out_pos < max_len - 4; i++) {
        int char_len = byte_to_unicode_char(bytes[i], output + out_pos, max_len - out_pos);
        if (char_len < 0) {
            return -1;
        }
        out_pos += char_len;
    }
    
    output[out_pos] = '\0';
    return out_pos;
}

/**
 * Convert unicode character back to byte value for GPT-2 decoding
 * Returns the byte value or -1 on error
 */
static int __attribute__((unused)) unicode_char_to_byte(uint32_t unicode_val) {
    if (!bpe_model || !bpe_model->bytes_to_unicode_initialized) {
        return -1;
    }
    
    // Use inverse mapping for values in range
    if (unicode_val < 512) {
        return bpe_model->unicode_to_bytes[unicode_val];
    }
    
    // For values outside range, search the forward mapping
    for (int i = 0; i < 256; i++) {
        if (bpe_model->bytes_to_unicode[i] == unicode_val) {
            return i;
        }
    }
    
    return -1;
}


/**
 * Initialize DPDK BPE model with memory pools and vocabulary
 */
int dpdk_bpe_init(unsigned int socket_id, bpe_model_type_t model_type) {
    bpe_set_error("");
    // Initialize vocabulary system first
    if (dpdk_vocab_init(socket_id) < 0) {
        RTE_LOG(ERR, BPE, "Failed to initialize vocabulary system\n");
        bpe_set_error("vocabulary init failed");
        return -1;
    }
    
    // Allocate model structure
    bpe_model = rte_zmalloc_socket("bpe_model", sizeof(bpe_model_t), 
                                   RTE_CACHE_LINE_SIZE, socket_id);
    if (!bpe_model) {
        RTE_LOG(ERR, BPE, "Failed to allocate BPE model\n");
        dpdk_vocab_cleanup();
        bpe_set_error("allocation failure: bpe_model");
        return -1;
    }
    
    // Allocate merges array
    bpe_model->merges = rte_zmalloc_socket("bpe_merges", 
                                           sizeof(bpe_merge_t) * MAX_MERGES,
                                           RTE_CACHE_LINE_SIZE, socket_id);
    if (!bpe_model->merges) {
        RTE_LOG(ERR, BPE, "Failed to allocate BPE merges array\n");
        rte_free(bpe_model);
        bpe_set_error("allocation failure: merges array");
        return -1;
    }
    
    // Allocate vocabulary array only for ModernBERT mode; GPT-2 uses external vocab table
    bpe_model->vocab = NULL;
    if (model_type != BPE_MODEL_GPT2) {
        bpe_model->vocab = rte_zmalloc_socket("bpe_vocab",
                                              sizeof(char[MAX_TOKEN_LEN]) * MAX_VOCAB_SIZE,
                                              RTE_CACHE_LINE_SIZE, socket_id);
        if (!bpe_model->vocab) {
            RTE_LOG(ERR, BPE, "Failed to allocate BPE vocabulary\n");
            rte_free(bpe_model->merges);
            rte_free(bpe_model);
            bpe_set_error("allocation failure: vocab array");
            return -1;
        }
    }
    
    // Create memory pool for tokens
    char pool_name[RTE_MEMPOOL_NAMESIZE];
    snprintf(pool_name, sizeof(pool_name), "bpe_token_pool_%u", socket_id);
    bpe_model->token_pool = rte_mempool_create(pool_name,
                                               BPE_MEMPOOL_SIZE,
                                               MAX_TOKEN_LEN,
                                               BPE_CACHE_SIZE,
                                               0,
                                               NULL, NULL,
                                               NULL, NULL,
                                               socket_id,
                                               0);
    if (!bpe_model->token_pool) {
        RTE_LOG(ERR, BPE, "Failed to create BPE token memory pool\n");
        rte_free(bpe_model->vocab);
        rte_free(bpe_model->merges);
        rte_free(bpe_model);
        bpe_set_error("mempool create failed: token_pool");
        return -1;
    }

    // Create hash table for merge lookups
    struct rte_hash_parameters hash_params = {
        .name = "bpe_merge_hash",
        .entries = MAX_MERGES,
        .key_len = sizeof(merge_key_t),  // Two tokens concatenated
        .hash_func = rte_jhash,
        .hash_func_init_val = 0,
        .socket_id = socket_id,
    };
    bpe_model->merge_hash = rte_hash_create(&hash_params);
    if (!bpe_model->merge_hash) {
        RTE_LOG(ERR, BPE, "Failed to create merge hash table\n");
        rte_mempool_free(bpe_model->token_pool);
        rte_free(bpe_model->vocab);
        rte_free(bpe_model->merges);
        rte_free(bpe_model);
        bpe_set_error("hash create failed: merge_hash");
        return -1;
    }
    
    // Initialize token cache (optional, can be disabled by capacity=0)
    const char* cap_env = getenv("DPDK_BPE_CACHE_CAPACITY");
    uint32_t cache_capacity = BPE_TOKEN_CACHE_DEFAULT_CAPACITY;
    if (cap_env && cap_env[0] != '\0') {
        long v = strtol(cap_env, NULL, 10);
        if (v >= 0 && v <= 10000000) cache_capacity = (uint32_t)v; // sane bound
    }
    bpe_model->token_cache_enabled = (cache_capacity > 0);
    bpe_model->token_cache_capacity = cache_capacity;
    bpe_model->token_cache_hash = NULL;
    bpe_model->token_cache_pool = NULL;
    if (bpe_model->token_cache_enabled) {
        char cache_hash_name[64];
        snprintf(cache_hash_name, sizeof(cache_hash_name), "bpe_token_cache_%u", socket_id);
        struct rte_hash_parameters cache_params = {
            .name = cache_hash_name,
            .entries = cache_capacity,
            .key_len = sizeof(token_cache_key_t),
            .hash_func = rte_jhash,
            .hash_func_init_val = 0,
            .socket_id = socket_id,
        };
        bpe_model->token_cache_hash = rte_hash_create(&cache_params);
        if (!bpe_model->token_cache_hash) {
            RTE_LOG(WARNING, BPE, "Failed to create token cache hash; disabling cache\n");
            bpe_model->token_cache_enabled = false;
        } else {
            char pool_name_cache[RTE_MEMPOOL_NAMESIZE];
            snprintf(pool_name_cache, sizeof(pool_name_cache), "bpe_cache_pool_%u", socket_id);
            bpe_model->token_cache_pool = rte_mempool_create(pool_name_cache,
                                                             cache_capacity,
                                                             sizeof(token_cache_entry_t),
                                                             BPE_CACHE_SIZE,
                                                             0,
                                                             NULL, NULL,
                                                             NULL, NULL,
                                                             socket_id,
                                                             0);
            if (!bpe_model->token_cache_pool) {
                RTE_LOG(WARNING, BPE, "Failed to create token cache pool; disabling cache\n");
                rte_hash_free(bpe_model->token_cache_hash);
                bpe_model->token_cache_hash = NULL;
                bpe_model->token_cache_enabled = false;
            } else {
                RTE_LOG(INFO, BPE, "Token cache enabled: capacity=%u, max_input_len=%u, entry_data=%u\n",
                        bpe_model->token_cache_capacity, (unsigned)BPE_TOKEN_CACHE_MAX_INPUT_LEN, (unsigned)BPE_TOKEN_CACHE_ENTRY_DATA);
            }
    }
    }
    
    // Initialize counters and model type
    bpe_model->num_merges = 0;
    bpe_model->vocab_size = 0;
    bpe_model->model_type = model_type;
    bpe_model->bytes_to_unicode_initialized = false;
    bpe_model->cache_lookups = 0;
    bpe_model->cache_hits = 0;
    bpe_model->cache_inserts = 0;
    bpe_model->cache_insert_fails = 0;
    bpe_model->cache_skip_longkey = 0;
    bpe_model->cache_skip_oversize = 0;
    bpe_model->produce_strings = true;
    bpe_model->id_merge_hash = NULL;
    bpe_model->id_merge_vals = NULL;
    bpe_model->num_id_merges = 0;
    
    // Initialize model-specific features
    if (model_type == BPE_MODEL_GPT2) {
        // Initialize bytes to unicode mapping for GPT-2
        init_bytes_to_unicode();
        // Set ByteLevel defaults and then override from tokenizer.json if present
        bl_set_gpt2_defaults();
        // Load ByteLevel flags and merges directly from tokenizer.json
        const char* tok_json_path = getenv("DPDK_BPE_TOKENIZER_JSON");
        char tok_json_resolved[512];
        if (!tok_json_path || tok_json_path[0] == '\0') {
            tok_json_path = DEFAULT_GPT2_TOKENIZER_JSON;
        }
        // Try to resolve tokenizer.json relative to common project roots
        FILE *tj = fopen(tok_json_path, "r");
        if (!tj) {
            const char *prefixes[] = {"../", "../../", "../../../", "../../../../"};
            for (size_t pi = 0; pi < sizeof(prefixes)/sizeof(prefixes[0]); ++pi) {
                snprintf(tok_json_resolved, sizeof(tok_json_resolved), "%s%s", prefixes[pi], tok_json_path);
                tj = fopen(tok_json_resolved, "r");
                if (tj) { tok_json_path = tok_json_resolved; break; }
            }
        }
        if (tj) fclose(tj);

        if (dpdk_bpe_load_tokenizer_config(tok_json_path) == 0) {
            RTE_LOG(INFO, BPE, "Loaded ByteLevel config from %s\n", tok_json_path);
        } else {
            RTE_LOG(WARNING, BPE, "ByteLevel config not loaded; using defaults\n");
        }
        bpe_model->num_merges = 0;
        rte_hash_reset(bpe_model->merge_hash);
        int mcount = dpdk_bpe_load_merges_from_tokenizer_json(tok_json_path);
        if (mcount <= 0) {
            RTE_LOG(WARNING, BPE, "No merges loaded from tokenizer.json (%s). Ensure model.merges exists.\n", tok_json_path);
        }
        RTE_LOG(INFO, BPE, "Initialized GPT-2 byte-level BPE model\n");
    } else {
        // Add basic ASCII characters to vocabulary for ModernBERT
        for (int i = 32; i < 127; i++) {
            if (bpe_model->vocab_size < MAX_VOCAB_SIZE) {
                bpe_model->vocab[bpe_model->vocab_size][0] = (char)i;
                bpe_model->vocab[bpe_model->vocab_size][1] = '\0';
                bpe_model->vocab_size++;
            }
        }
        RTE_LOG(INFO, BPE, "Initialized ModernBERT BPE model with %d vocabulary entries\n", 
                bpe_model->vocab_size);
    }
    return 0;
}

/**
 * Cleanup DPDK BPE model and free resources
 */
void dpdk_bpe_cleanup(void) {
    if (bpe_model) {
        if (bpe_model->token_pool) {
            rte_mempool_free(bpe_model->token_pool);
        }
        if (bpe_model->merge_hash) {
            rte_hash_free(bpe_model->merge_hash);
        }
        if (bpe_model->token_cache_hash) {
            rte_hash_free(bpe_model->token_cache_hash);
        }
        if (bpe_model->token_cache_pool) {
            rte_mempool_free(bpe_model->token_cache_pool);
        }
        if (bpe_model->vocab) {
            rte_free(bpe_model->vocab);
        }
        if (bpe_model->merges) {
            rte_free(bpe_model->merges);
        }
        rte_free(bpe_model);
        bpe_model = NULL;
    }
    
    // Cleanup vocabulary system
    dpdk_vocab_cleanup();
    
    RTE_LOG(INFO, BPE, "DPDK BPE model cleaned up\n");
}

/**
 * Add a merge rule to the BPE model using DPDK memory
 */
int dpdk_bpe_add_merge(const char* first, const char* second, int priority) {
    if (!bpe_model) {
        RTE_LOG(ERR, BPE, "BPE model not initialized\n");
        return -1;
    }
    
    if (bpe_model->num_merges >= MAX_MERGES) {
        RTE_LOG(ERR, BPE, "Maximum number of merges reached\n");
        return -1;
    }
    
    bpe_merge_t* merge = &bpe_model->merges[bpe_model->num_merges];
    rte_strscpy(merge->first, first, MAX_TOKEN_LEN);
    rte_strscpy(merge->second, second, MAX_TOKEN_LEN);
    merge->priority = priority;
    
    // Create compact hash key
    merge_key_t key;
    key.ha = bpe_token_hash(first);
    key.hb = bpe_token_hash(second);
    
    // Add to hash table (store index of the merge)
    int32_t ret = rte_hash_add_key_data(bpe_model->merge_hash, &key,
                                         (void*)(uintptr_t)bpe_model->num_merges);
    if (ret < 0) {
        RTE_LOG(WARNING, BPE, "Failed to add merge to hash table: %s, %s\n", first, second);
    }
    
    bpe_model->num_merges++;
    
    RTE_LOG(DEBUG, BPE, "Added merge rule: '%s' + '%s' (priority: %d)\n",
            first, second, priority);
    
    return 0;
}

/**
 * Check if a character is punctuation that should be split
 */
static bool is_split_char(char c) {
    return (c == '!' || c == '?' || c == '.' || c == ',' || c == ';' || c == ':' || 
            c == '"' || c == '\'' || c == '(' || c == ')' || c == '[' || c == ']' || 
            c == '{' || c == '}' || c == '-' || c == '_');
}

/**
 * Pre-tokenize text into word-level tokens with space markers and punctuation splitting
 * This matches the behavior of modern BPE tokenizers like ModernBERT
 */
static int dpdk_pre_tokenize(const char* text, char tokens[][MAX_TOKEN_LEN]) {
    int len = strlen(text);
    int token_count = 0;
    int i = 0;
    
    while (i < len && token_count < MAX_TOKENS) {
        // Skip whitespace
        while (i < len && (text[i] == ' ' || text[i] == '\t' || text[i] == '\n')) {
            i++;
        }
        
        if (i >= len) break;
        
        // Determine if this should have a space marker
        bool needs_space_marker = (token_count > 0);
        
        // Handle punctuation - each punctuation mark is its own token
        if (is_split_char(text[i])) {
            if (needs_space_marker) {
                // Prefix the punctuation with the GPT-2 continuation marker
                memcpy(tokens[token_count], GPT2_CONT_PREFIX, GPT2_CONT_PREFIX_LEN);
                tokens[token_count][GPT2_CONT_PREFIX_LEN] = text[i];
                tokens[token_count][GPT2_CONT_PREFIX_LEN + 1] = '\0';
            } else {
                tokens[token_count][0] = text[i];
                tokens[token_count][1] = '\0';
            }
            token_count++;
            i++;
            continue;
        }
        
        // Handle regular word
        int word_start = i;
        while (i < len && !is_split_char(text[i]) && 
               text[i] != ' ' && text[i] != '\t' && text[i] != '\n') {
            i++;
        }
        
        if (i > word_start) {
            int word_len = i - word_start;
            if (word_len < MAX_TOKEN_LEN - GPT2_CONT_PREFIX_LEN) {  // Leave room for prefix
                if (needs_space_marker) {
                    memcpy(tokens[token_count], GPT2_CONT_PREFIX, GPT2_CONT_PREFIX_LEN);
                    memcpy(&tokens[token_count][GPT2_CONT_PREFIX_LEN], &text[word_start], word_len);
                    tokens[token_count][word_len + GPT2_CONT_PREFIX_LEN] = '\0';
                } else {
                    strncpy(tokens[token_count], &text[word_start], word_len);
                    tokens[token_count][word_len] = '\0';
                }
                token_count++;
            }
        }
    }
    
    return token_count;
}

// Return the length in bytes of the next UTF-8 code point starting at p.
// Falls back to 1 on malformed leading byte.
static inline int utf8_cp_len(const unsigned char* p) {
    if ((*p & 0x80) == 0x00) return 1;           // 0xxxxxxx
    if ((*p & 0xE0) == 0xC0) return 2;           // 110xxxxx
    if ((*p & 0xF0) == 0xE0) return 3;           // 1110xxxx
    if ((*p & 0xF8) == 0xF0) return 4;           // 11110xxx
    return 1; // conservative fallback
}

// trim in-place
static inline void trim_line(char *s) {
    if (!s) return;
    int n = (int)strlen(s);
    while (n > 0 && (s[n-1] == '\n' || s[n-1] == '\r' || s[n-1] == ' ' || s[n-1] == '\t')) s[--n] = '\0';
    int lead = 0; while (s[lead] == ' ' || s[lead] == '\t') lead++;
    if (lead > 0) memmove(s, s + lead, strlen(s + lead) + 1);
}

/**
 * Split a token into individual characters for BPE merging.
 * For GPT-2, tokens from dpdk_gpt2_split_text are already in unicode form
 * where each UTF-8 character represents one original byte.
 * We split by UTF-8 characters, not raw bytes.
 */
static int dpdk_split_token_to_chars(const char* token, char subtokens[][MAX_TOKEN_LEN]) {
    int len = strlen(token);
    int subtoken_count = 0;
    int i = 0;
    
    // Split by UTF-8 characters (each character represents an original byte already encoded)
    while (i < len && subtoken_count < MAX_TOKENS) {
        const unsigned char* p = (const unsigned char*)token + i;
        int char_len = utf8_cp_len(p);
        if (char_len < 1) char_len = 1; // safety
        if (i + char_len > len) char_len = len - i; // clamp if truncated
        
        // Copy this UTF-8 character into its own subtoken
        if (char_len < MAX_TOKEN_LEN) {
            memcpy(subtokens[subtoken_count], token + i, char_len);
            subtokens[subtoken_count][char_len] = '\0';
            subtoken_count++;
        }
        i += char_len;
    }
    
    return subtoken_count;
}

/**
 * Find the highest priority merge that can be applied
 */
// Helper: get pair rank from precomputed hashes; returns INT32_MAX if no merge exists.
static inline int dpdk_pair_rank(uint32_t ha, uint32_t hb) {
    merge_key_t key; key.ha = ha; key.hb = hb;
    void* data;
    if (rte_hash_lookup_data(bpe_model->merge_hash, &key, &data) >= 0) {
        int merge_idx = (int)(uintptr_t)data;
        return bpe_model->merges[merge_idx].priority;
    }
    return INT32_MAX;
}

typedef struct { uint32_t a; uint32_t b; } id_pair_key_t;

// Lookup rank and new_id for an ID pair; returns INT32_MAX if no merge.
static inline int dpdk_pair_rank_id(uint32_t ida, uint32_t idb, uint32_t* out_new_id) {
    if (!bpe_model->id_merge_hash) return INT32_MAX;
    id_pair_key_t key; key.a = ida; key.b = idb;
    void* data = NULL;
    if (rte_hash_lookup_data(bpe_model->id_merge_hash, &key, &data) >= 0 && data) {
        const typeof(*bpe_model->id_merge_vals)* v = (const typeof(*bpe_model->id_merge_vals)*)data;
        if (out_new_id) *out_new_id = v->new_id;
        return v->rank;
    }
    return INT32_MAX;
}

// Min-heap of pairs: (rank, pos)
typedef struct {
    int rank;
    int pos;  // position in the current linked sequence
} pair_item_t;

typedef struct {
    pair_item_t arr[MAX_TOKENS * 2];
    int size;
} pair_heap_t;

static inline void heap_swap(pair_item_t* a, pair_item_t* b) {
    pair_item_t t = *a; *a = *b; *b = t;
}

static inline void heap_push(pair_heap_t* h, int rank, int pos) {
    if (rank == INT32_MAX) return; // only track valid merges
    int i = h->size++;
    h->arr[i].rank = rank; h->arr[i].pos = pos;
    // sift up
    while (i > 0) {
        int p = (i - 1) >> 1;
        if (h->arr[p].rank <= h->arr[i].rank) break;
        heap_swap(&h->arr[p], &h->arr[i]);
        i = p;
    }
}

static inline int heap_pop(pair_heap_t* h, pair_item_t* out) {
    if (h->size == 0) return 0;
    *out = h->arr[0];
    h->arr[0] = h->arr[--h->size];
    // sift down
    int i = 0;
    while (1) {
        int l = (i << 1) + 1, r = l + 1, m = i;
        if (l < h->size && h->arr[l].rank < h->arr[m].rank) m = l;
        if (r < h->size && h->arr[r].rank < h->arr[m].rank) m = r;
        if (m == i) break;
        heap_swap(&h->arr[i], &h->arr[m]);
        i = m;
    }
    return 1;
}

// Apply a merge at the specified position using optimized memory operations

// Decode next UTF-8 code point. Returns bytes consumed; sets *out_cp. On malformed, returns 1 and sets raw byte.
static inline int utf8_next_cp(const unsigned char* s, int len, int i, uint32_t* out_cp) {
    unsigned char c = s[i];
    if ((c & 0x80) == 0x00) { *out_cp = c; return 1; }
    if (i + 1 < len && (c & 0xE0) == 0xC0) { // 2-byte
        *out_cp = ((uint32_t)(c & 0x1F) << 6) | (uint32_t)(s[i+1] & 0x3F);
        return 2;
    }
    if (i + 2 < len && (c & 0xF0) == 0xE0) { // 3-byte
        *out_cp = ((uint32_t)(c & 0x0F) << 12) | ((uint32_t)(s[i+1] & 0x3F) << 6) | (uint32_t)(s[i+2] & 0x3F);
        return 3;
    }
    if (i + 3 < len && (c & 0xF8) == 0xF0) { // 4-byte
        *out_cp = ((uint32_t)(c & 0x07) << 18) | ((uint32_t)(s[i+1] & 0x3F) << 12) | ((uint32_t)(s[i+2] & 0x3F) << 6) | (uint32_t)(s[i+3] & 0x3F);
        return 4;
    }
    *out_cp = c; // malformed fallback
    return 1;
}

// Return true if cp is a Unicode letter (\p{L}) in common scripts used here (Latin, CJK, Kana, Hangul, etc.)
static inline bool is_letter_cp(uint32_t cp) {
    // ASCII letters
    if ((cp >= 'A' && cp <= 'Z') || (cp >= 'a' && cp <= 'z')) return true;
    // Latin-1 letters (basic approximation)
    if ((cp >= 0x00C0 && cp <= 0x00D6) || (cp >= 0x00D8 && cp <= 0x00F6) || (cp >= 0x00F8 && cp <= 0x024F)) return true;
    // CJK Unified Ideographs & Extensions (subset ranges)
    if ((cp >= 0x3400 && cp <= 0x4DBF) || (cp >= 0x4E00 && cp <= 0x9FFF) || (cp >= 0x20000 && cp <= 0x2A6DF)) return true;
    // Hiragana, Katakana
    if ((cp >= 0x3040 && cp <= 0x309F) || (cp >= 0x30A0 && cp <= 0x30FF)) return true;
    // Hangul syllables
    if (cp >= 0xAC00 && cp <= 0xD7AF) return true;
    // Fullwidth Latin letters
    if ((cp >= 0xFF21 && cp <= 0xFF3A) || (cp >= 0xFF41 && cp <= 0xFF5A)) return true;
    return false;
}

static inline bool is_number_cp(uint32_t cp) {
    // ASCII digits and fullwidth digits
    return (cp >= '0' && cp <= '9') || (cp >= 0xFF10 && cp <= 0xFF19);
}

static int dpdk_gpt2_split_text(const char* text, char tokens[][MAX_TOKEN_LEN], int max_tokens) {
    if (!text || !tokens || !bpe_model || !bpe_model->bytes_to_unicode_initialized) {
        return -1;
    }

    const unsigned char* s = (const unsigned char*)text;
    int len = (int)strlen(text);
    int token_count = 0;
    int i = 0;

    while (i < len && token_count < max_tokens) {
        // The GPT-2 regex pattern is: ' ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+'
        // This means: optional space followed by content, or whitespace sequences
        
        // Handle spaces - GPT-2 pattern: ' ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+'
        // This means spaces before letters/numbers/punctuation attach to them
        // But standalone whitespace sequences are kept separate
        bool had_space = false;
        if (s[i] == ' ') {
            // Look ahead to see what follows
            int j = i;
            while (j < len && s[j] == ' ') j++;
            
            // Check what comes after the spaces
            bool followed_by_content = (j < len && s[j] != '\n' && s[j] != '\r' && s[j] != '\t');
            
            if (followed_by_content) {
                // Spaces before content: emit all but last space separately, attach last space to content
                int spaces_to_emit = (j - i) - 1;  // All spaces except the last one
                while (spaces_to_emit > 0) {
                    uint8_t space_byte = ' ';
                    bytes_to_unicode_string(&space_byte, 1, tokens[token_count], MAX_TOKEN_LEN);
                    token_count++;
                    i++;
                    spaces_to_emit--;
                }
                // Now i points to the last space, which will attach to the following content
                had_space = true;
                i++;
            } else {
                // Trailing spaces (at end or before newline) - emit all separately
                while (i < j) {
                    uint8_t space_byte = ' ';
                    bytes_to_unicode_string(&space_byte, 1, tokens[token_count], MAX_TOKEN_LEN);
                    token_count++;
                    i++;
                }
            }
            
            if (i >= len || s[i] == '\n' || s[i] == '\r' || s[i] == '\t') {
                continue;
            }
        }

        // Check if we're at whitespace (newlines, tabs, etc) - group consecutive same-type whitespace
        if (i < len && (s[i] == '\n' || s[i] == '\r' || s[i] == '\t')) {
            uint8_t ws_bytes[MAX_TOKEN_LEN];
            int ws_len = 0;
            unsigned char ws_char = s[i];
            while (i < len && s[i] == ws_char && ws_len < MAX_TOKEN_LEN) {
                ws_bytes[ws_len++] = s[i];
                i++;
            }
            bytes_to_unicode_string(ws_bytes, ws_len, tokens[token_count], MAX_TOKEN_LEN);
            token_count++;
            continue;
        }
        
        // Peek category of the next code point
        uint32_t cp; int cp_len = utf8_next_cp(s, len, i, &cp);
        bool isL = is_letter_cp(cp);
        bool isN = is_number_cp(cp);

        // Special-case GPT-2 contractions: 's|'t|'re|'ve|'m|'ll|'d
        // Trigger only when the next char is an ASCII apostrophe and it is NOT preceded by a space.
        if (cp == '\'' && (i == 0 || s[i-1] != ' ')) {
            // Check for the allowed suffixes in ASCII
            const char *suffixes[] = {"s", "t", "re", "ve", "m", "ll", "d"};
            int suffix_lens[]      = {  1 ,   1 ,   2  ,   2  ,  1 ,   2  ,  1  };
            int matched = -1;
            for (int si = 0; si < 7; ++si) {
                int sl = suffix_lens[si];
                if (i + 1 + sl <= len) {
                    bool ok = true;
                    for (int k = 0; k < sl; ++k) {
                        unsigned char c = s[i + 1 + k];
                        if (!(c >= 'a' && c <= 'z')) { ok = false; break; }
                    }
                    if (ok && strncmp((const char*)&s[i+1], suffixes[si], sl) == 0) {
                        matched = si;
                        break;
                    }
                }
            }
            if (matched != -1) {
                // Emit "'<suffix>" as its own chunk (no space prefix for this branch)
                uint8_t chunk_bytes[MAX_TOKEN_LEN];
                int chunk_len = 0;
                chunk_bytes[chunk_len++] = '\'';
                int sl = suffix_lens[matched];
                if (chunk_len + sl < MAX_TOKEN_LEN) {
                    memcpy(&chunk_bytes[chunk_len], &s[i+1], sl);
                    chunk_len += sl;
                }
                bytes_to_unicode_string(chunk_bytes, chunk_len, tokens[token_count], MAX_TOKEN_LEN);
                token_count++;
                i += 1 + sl;
                continue; // start next chunk
            }
        }

        // Collect a chunk: letters+, numbers+, or punctuation/special+ (no spaces inside)
        uint8_t chunk_bytes[MAX_TOKEN_LEN];
        int chunk_len = 0;
        
        // Add the space prefix if we had one (not for indentation)
        if (had_space && chunk_len < MAX_TOKEN_LEN) {
            chunk_bytes[chunk_len++] = ' ';
        }
        

        if (isL) {
            // Letters+
            do {
                // append original UTF-8 bytes
                if (chunk_len + cp_len >= MAX_TOKEN_LEN - 1) break;
                memcpy(&chunk_bytes[chunk_len], &s[i], cp_len);
                chunk_len += cp_len;
                i += cp_len;
                if (i >= len) break;
                cp_len = utf8_next_cp(s, len, i, &cp);
            } while (is_letter_cp(cp));
        } else if (isN) {
            // Numbers+
            do {
                if (chunk_len + cp_len >= MAX_TOKEN_LEN - 1) break;
                memcpy(&chunk_bytes[chunk_len], &s[i], cp_len);
                chunk_len += cp_len;
                i += cp_len;
                if (i >= len) break;
                cp_len = utf8_next_cp(s, len, i, &cp);
            } while (is_number_cp(cp));
        } else {
            // Other (punctuation/symbol) +, but stop at spaces and newlines
            do {
                if (cp == ' ' || cp == '\n') break; // Stop at whitespace
                if (chunk_len + cp_len >= MAX_TOKEN_LEN - 1) break;
                memcpy(&chunk_bytes[chunk_len], &s[i], cp_len);
                chunk_len += cp_len;
                i += cp_len;
                if (i >= len) break;
                cp_len = utf8_next_cp(s, len, i, &cp);
            } while (cp != ' ' && cp != '\n' && !is_letter_cp(cp) && !is_number_cp(cp));
        }

        if (chunk_len > 0) {
            bytes_to_unicode_string(chunk_bytes, chunk_len, tokens[token_count], MAX_TOKEN_LEN);
            token_count++;
        }
    }

    return token_count;
}

/**
 * Perform BPE tokenization on input text using DPDK optimizations
 * 
 * @param text Input text to tokenize
 * @param tokens Output array to store tokens
 * @param max_tokens Maximum number of tokens to generate
 * @return Number of tokens generated, or -1 on error
 */
int dpdk_bpe_tokenize(const char* text, char tokens[][MAX_TOKEN_LEN], int token_ids[], int max_tokens) {
    if (unlikely(!bpe_model)) {
        RTE_LOG(ERR, BPE, "BPE model not initialized\n");
        return -1;
    }
    
    if (unlikely(!text || !tokens || !token_ids || max_tokens <= 0)) {
        RTE_LOG(ERR, BPE, "Invalid parameters for tokenization\n");
        return -1;
    }
    
    // No full-sequence cache; follow Rust's per-pre-token cache behavior

    // Step 1: Pre-tokenize text based on model type
    // Allocate large pre-token buffer on the heap to avoid stack overflow
    char (*pre_tokens)[MAX_TOKEN_LEN] = rte_zmalloc_socket(
        "bpe_pre_tokens", (size_t)MAX_TOKENS * (size_t)MAX_TOKEN_LEN,
        RTE_CACHE_LINE_SIZE, rte_socket_id());
    if (!pre_tokens) {
        RTE_LOG(ERR, BPE, "Allocation failed for pre_tokens buffer\n");
        return -1;
    }
    int pre_token_count;
    
    if (bpe_model->model_type == BPE_MODEL_GPT2) {
        // GPT-2 style: split text with special handling for spaces
        pre_token_count = dpdk_gpt2_split_text(text, pre_tokens, MAX_TOKENS);
        if (pre_token_count < 0) { rte_free(pre_tokens); return -1; }
    } else {
        // ModernBERT style: standard pre-tokenization
        pre_token_count = dpdk_pre_tokenize(text, pre_tokens);
    }
    
    if (unlikely(pre_token_count > max_tokens)) {
        RTE_LOG(ERR, BPE, "Too many tokens for output buffer\n");
        rte_free(pre_tokens);
        return -1;
    }
    
    // Step 2: Process each pre-token
    int final_token_count = 0;
    
    for (int i = 0; i < pre_token_count && final_token_count < max_tokens; i++) {
        // Try token cache lookup for this pre-token
        int out_start = final_token_count;
        if (bpe_model->token_cache_enabled && bpe_model->token_cache_hash && bpe_model->token_cache_pool) {
            int pretok_len = (int)strnlen(pre_tokens[i], MAX_TOKEN_LEN);
            if (pretok_len > 0 && pretok_len <= (int)BPE_TOKEN_CACHE_MAX_INPUT_LEN) {
                bpe_model->cache_lookups++;
                token_cache_key_t k; token_cache_make_key(pre_tokens[i], pretok_len, &k);
                void* v = NULL;
                if (rte_hash_lookup_data(bpe_model->token_cache_hash, &k, &v) >= 0 && v != NULL) {
                    bpe_model->cache_hits++;
                    token_cache_entry_t* e = (token_cache_entry_t*)v;
                    const uint32_t* ids_cached = (const uint32_t*)e->data;
                    for (int t = 0; t < e->count && final_token_count < max_tokens; t++) {
                        token_ids[final_token_count] = (int)ids_cached[t];
                        if (bpe_model->produce_strings) {
                            const char* tk = dpdk_vocab_id_to_token(token_ids[final_token_count]);
                            rte_strscpy(tokens[final_token_count], tk, MAX_TOKEN_LEN);
                        } else {
                            tokens[final_token_count][0] = '\0';
                        }
                        final_token_count++;
                    }
                    // Served from cache, go to next pre-token
                    continue;
                }
            } else {
                if (pretok_len > (int)BPE_TOKEN_CACHE_MAX_INPUT_LEN)
                    bpe_model->cache_skip_longkey++;
            }
        }

        // Split into characters (UTF-8 codepoints) and map to initial token IDs
        const char* pt = pre_tokens[i];
        int pt_len = (int)strnlen(pt, MAX_TOKEN_LEN);
        uint32_t ids[MAX_TOKENS];
        int offsets[MAX_TOKENS];
        uint8_t lens_b[MAX_TOKENS];
        int slot_count = 0;
        for (int off = 0; off < pt_len && slot_count < MAX_TOKENS; ) {
            const unsigned char* p = (const unsigned char*)pt + off;
            int cp_len = utf8_cp_len(p);
            if (cp_len < 1) cp_len = 1;
            if (off + cp_len > pt_len) cp_len = pt_len - off;
            offsets[slot_count] = off;
            lens_b[slot_count] = (uint8_t)cp_len;
            // Lookup ID for this character token without storing a persistent string
            char tmp[MAX_TOKEN_LEN];
            memcpy(tmp, pt + off, (size_t)cp_len);
            tmp[cp_len] = '\0';
            int id = dpdk_vocab_token_to_id(tmp);
            ids[slot_count] = (id >= 0) ? (uint32_t)id : 0;
            slot_count++;
            off += cp_len;
        }
        if (slot_count <= 0) continue;

        // Build position linked-list over slots (0..slot_count-1)
        int idxs[MAX_TOKENS];
        int left_pos[MAX_TOKENS];
        int right_pos[MAX_TOKENS];
        uint8_t alive[MAX_TOKENS];
        for (int p = 0; p < slot_count; p++) {
            idxs[p] = p;
            left_pos[p] = (p == 0) ? -1 : (p - 1);
            right_pos[p] = (p == slot_count - 1) ? -1 : (p + 1);
            alive[p] = 1;
        }
        int head = 0;

        // Initialize heap with all existing adjacent ID pairs
        pair_heap_t heap; heap.size = 0;
        for (int p = 0; p < slot_count - 1; p++) {
            int li = idxs[p];
            int ri = idxs[p + 1];
            uint32_t tmp_new = 0;
            int rank = dpdk_pair_rank_id(ids[li], ids[ri], &tmp_new);
            if (rank != INT32_MAX) heap_push(&heap, rank, p);
        }

        // Greedy merging via heap with lazy invalidation
        pair_item_t top;
        int safety = 0;
        while (heap_pop(&heap, &top)) {
            int pos = top.pos;
            if (pos < 0 || pos >= slot_count || !alive[pos]) continue;
            int rpos = right_pos[pos];
            if (rpos < 0 || !alive[rpos]) continue;

            int li = idxs[pos];
            int ri = idxs[rpos];
            uint32_t new_id = 0;
            int cur_rank = dpdk_pair_rank_id(ids[li], ids[ri], &new_id);
            if (cur_rank == INT32_MAX) continue; // pair no longer valid
            if (cur_rank != top.rank) { // priority changed; requeue with current rank
                heap_push(&heap, cur_rank, pos);
                continue;
            }
            // Merge: write new ID into left slot
            ids[li] = new_id;

            // Remove rpos from linked list
            int nr = right_pos[rpos];
            right_pos[pos] = nr;
            if (nr != -1) left_pos[nr] = pos;
            alive[rpos] = 0;

            // Update head if needed (pos always survives, so head unchanged)

            // Add/refresh neighboring pairs
            int lp = left_pos[pos];
            if (lp != -1 && alive[lp]) {
                int l_li = idxs[lp];
                int l_ri = idxs[pos];
                uint32_t tmp_new2 = 0;
                int rr = dpdk_pair_rank_id(ids[l_li], ids[l_ri], &tmp_new2);
                if (rr != INT32_MAX) heap_push(&heap, rr, lp);
            }
            int rp = right_pos[pos];
            if (rp != -1 && alive[rp]) {
                int r_li = idxs[pos];
                int r_ri = idxs[rp];
                uint32_t tmp_new3 = 0;
                int rr = dpdk_pair_rank_id(ids[r_li], ids[r_ri], &tmp_new3);
                if (rr != INT32_MAX) heap_push(&heap, rr, pos);
            }

            if (unlikely(++safety > MAX_TOKENS * 8)) {
                RTE_LOG(WARNING, BPE, "Merge safety cap reached; breaking\n");
                break;
            }
        }

        // Emit results by traversing from head across alive positions
        int p = head;
        while (p != -1 && final_token_count < max_tokens) {
            if (alive[p]) {
                int si = idxs[p];
                token_ids[final_token_count] = (int)ids[si];
                if (bpe_model->produce_strings) {
                    const char* tk = dpdk_vocab_id_to_token(token_ids[final_token_count]);
                    rte_strscpy(tokens[final_token_count], tk, MAX_TOKEN_LEN);
                } else {
                    tokens[final_token_count][0] = '\0';
                }
                final_token_count++;
            }
            p = right_pos[p];
        }

        // Insert produced sequence into cache if enabled and small enough
        if (bpe_model->token_cache_enabled && bpe_model->token_cache_hash && bpe_model->token_cache_pool) {
            int pretok_len = (int)strnlen(pre_tokens[i], MAX_TOKEN_LEN);
            int produced = final_token_count - out_start;
            if (produced > 0 && pretok_len > 0 && pretok_len <= (int)BPE_TOKEN_CACHE_MAX_INPUT_LEN) {
                int bytes = produced * (int)sizeof(uint32_t);
                if (bytes <= (int)BPE_TOKEN_CACHE_ENTRY_DATA) {
                    token_cache_entry_t* e = NULL;
                    if (rte_mempool_get(bpe_model->token_cache_pool, (void**)&e) == 0 && e) {
                        e->count = (uint16_t)produced;
                        memcpy(e->data, &token_ids[out_start], (size_t)bytes);
                        token_cache_key_t k; token_cache_make_key(pre_tokens[i], pretok_len, &k);
                        int32_t add_ret = rte_hash_add_key_data(bpe_model->token_cache_hash, &k, e);
                        if (add_ret < 0) {
                            rte_mempool_put(bpe_model->token_cache_pool, e);
                            bpe_model->cache_insert_fails++;
                        }
                        else {
                            bpe_model->cache_inserts++;
                        }
                    }
                }
                else {
                    bpe_model->cache_skip_oversize++;
                }
            }
        }
    }
    // Post-processing: For display purposes only, show Ġ prefix on first token if requested
    // NOTE: The actual tokenization should already have the correct form
    // This is just for display consistency with Python tokenizers
    // DO NOT modify token_ids as they should already be correct
    
    // (No full-sequence cache insertion)
    // RTE_LOG(DEBUG, BPE, "Tokenized '%s' into %d tokens\n", text, final_token_count);
    rte_free(pre_tokens);
    return final_token_count;
}

/**
 * Perform BPE tokenization with token ID output using vocabulary lookup
 */
int dpdk_bpe_tokenize_with_ids(const char* text, char tokens[][MAX_TOKEN_LEN], 
                               int token_ids[], int max_tokens) {
    // Simply call dpdk_bpe_tokenize which now handles both tokens and IDs
    return dpdk_bpe_tokenize(text, tokens, token_ids, max_tokens);
}

/**
 * Load BPE merges from a file with DPDK memory management
 * Expected format:
 *   - ModernBERT: each line contains "first_token second_token priority"
 *   - GPT-2: each line contains "first_token second_token" (priority assigned by order)
 */
int dpdk_bpe_load_merges_from_file(const char* filename, bool is_gpt2_format) {
    if (unlikely(!bpe_model)) {
        RTE_LOG(ERR, BPE, "BPE model not initialized\n");
        return -1;
    }

    FILE* file = fopen(filename, "r");
    if (unlikely(!file)) {
        RTE_LOG(ERR, BPE, "Failed to open merge file: %s\n", filename);
        return -1;
    }

    char line[512];
    char first[MAX_TOKEN_LEN], second[MAX_TOKEN_LEN];
    int priority;
    int loaded_merges = 0;
    int line_number = 0;
    int rank = 0;  // GPT-2 rank counter: increments only when a merge is added


    while (fgets(line, sizeof(line), file) && bpe_model->num_merges < MAX_MERGES) {
        line_number++;

        if (is_gpt2_format) {
            // Handle UTF-8 BOM on the first line if present
            if (line_number == 1 && (unsigned char)line[0] == 0xEF && (unsigned char)line[1] == 0xBB && (unsigned char)line[2] == 0xBF) {
                memmove(line, line + 3, strlen(line + 3) + 1);
            }
            trim_line(line);
            if (line[0] == '\0') continue;   // skip blanks
            if (line[0] == '#') continue;  // after trim, leading spaces removed

            if (sscanf(line, "%127s %127s", first, second) == 2) {
                priority = rank;
                if (dpdk_bpe_add_merge(first, second, priority) == 0) {
                    loaded_merges++;
                    rank++;
                }
            }
        } else {
            trim_line(line);
            if (line[0] == '\0') continue;
            if (line[0] == '#') continue;
            if (sscanf(line, "%127s %127s %d", first, second, &priority) == 3) {
                if (dpdk_bpe_add_merge(first, second, priority) == 0) {
                    loaded_merges++;
                }
            }
        }
    }

    fclose(file);

    RTE_LOG(INFO, BPE, "Loaded %d merge rules from %s\n", loaded_merges, filename);

    return loaded_merges;
}

/**
 * Load vocabulary from file with DPDK hash table
 */
int dpdk_bpe_load_vocab_from_file(const char* filename, bool is_json_format) {
    if (unlikely(!bpe_model)) {
        RTE_LOG(ERR, BPE, "BPE model not initialized\n");
        return -1;
    }
    
    int loaded_tokens;
    if (is_json_format) {
        // Load GPT-2 style JSON vocabulary
        RTE_LOG(INFO, BPE, "Loading vocabulary from JSON file: %s\n", filename);
        loaded_tokens = dpdk_vocab_load_from_json(filename);
    } else {
        // Load ModernBERT style line-based vocabulary
        RTE_LOG(INFO, BPE, "Loading vocabulary from line-based file: %s\n", filename);
        loaded_tokens = dpdk_vocab_load_from_file(filename);
    }
    
    if (loaded_tokens > 0) {
        RTE_LOG(INFO, BPE, "Loaded %d vocabulary tokens from %s\n", loaded_tokens, filename);
    }
    // After vocab is loaded, build ID-based merge map if possible
    dpdk_bpe_finalize_id_merges();
    return loaded_tokens;
}

/**
 * Get the current vocabulary size
 */
int dpdk_bpe_get_vocab_size(void) {
    if (unlikely(!bpe_model)) {
        return -1;
    }
    
    // Return vocabulary system size, not the old basic vocab size
    int vocab_size = dpdk_vocab_get_size();
    return vocab_size > 0 ? vocab_size : bpe_model->vocab_size;
}

/**
 * Get the number of loaded merge rules
 */
int dpdk_bpe_get_merge_count(void) {
    if (unlikely(!bpe_model)) {
        return -1;
    }
    return bpe_model->num_merges;
}

/**
 * Get BPE model statistics
 */
int dpdk_bpe_get_stats(struct bpe_stats *stats) {
    if (unlikely(!bpe_model || !stats)) {
        return -1;
    }
    
    stats->vocab_size = bpe_model->vocab_size;
    stats->merge_count = bpe_model->num_merges;
    stats->token_pool_size = BPE_MEMPOOL_SIZE;
    stats->token_pool_free = rte_mempool_avail_count(bpe_model->token_pool);
    
    return 0;
}

// Removed the duplicate definition of struct bpe_stats. Ensure the header file containing its definition is included.

// ByteLevel defaults and config loader
static void bl_set_gpt2_defaults(void) {
    // GPT-2 default behavior (matching provided tokenizer.json):
    // pre_tokenizer:  add_prefix_space=false, trim_offsets=true
    // post_processor: add_prefix_space=true,  trim_offsets=false
    // decoder:        add_prefix_space=true,  trim_offsets=true
    if (!bpe_model) return;
    bpe_model->bl_pre_add_prefix_space  = false;
    bpe_model->bl_pre_trim_offsets      = true;
    bpe_model->bl_post_add_prefix_space = true;
    bpe_model->bl_post_trim_offsets     = false;
    bpe_model->bl_dec_add_prefix_space  = true;
    bpe_model->bl_dec_trim_offsets      = true;
}

// TODO: use proper JSON parser
// naive JSON bool reader: finds key between start_ptr and end of buffer
static bool json_find_bool(const char* start_ptr, const char* key, bool* out_val) {
    if (!start_ptr || !key || !out_val) return false;
    const char* p = start_ptr;
    size_t klen = strlen(key);
    while ((p = strstr(p, key)) != NULL) {
        p += klen;
        // seek to ':'
        while (*p && *p != ':') p++;
        if (*p != ':') break;
        p++;
        // skip spaces
        while (*p == ' ' || *p == '\t') p++;
        if (strncmp(p, "true", 4) == 0) { *out_val = true; return true; }
        if (strncmp(p, "false", 5) == 0) { *out_val = false; return true; }
    }
    return false;
}

// returns pointer to section start of a component
static const char* json_find_section(const char* buf, const char* section_key) {
    if (!buf || !section_key) return NULL;
    const char* p = strstr(buf, section_key);
    if (!p) return NULL;
    // move to first '{' after the section key
    p = strchr(p, '{');
    return p;
}

int dpdk_bpe_load_tokenizer_config(const char* filename) {
    if (!bpe_model || !filename) return -1;
    FILE* f = fopen(filename, "rb");
    if (!f) return -1;
    // read file into buffer (cap at ~512KB)
    const size_t MAXJ = 512*1024;
    char* buf = (char*)malloc(MAXJ + 1);
    if (!buf) { fclose(f); return -1; }
    size_t n = fread(buf, 1, MAXJ, f);
    fclose(f);
    buf[n] = '\0';

    // Start with safe defaults
    bl_set_gpt2_defaults();

    // Locate sections
    const char* pre  = json_find_section(buf, "\"pre_tokenizer\"");
    const char* post = json_find_section(buf, "\"post_processor\"");
    const char* dec  = json_find_section(buf, "\"decoder\"");

    bool v;
    if (pre) {
        if (json_find_bool(pre, "\"add_prefix_space\"", &v)) bpe_model->bl_pre_add_prefix_space = v;
        if (json_find_bool(pre, "\"trim_offsets\"", &v))     bpe_model->bl_pre_trim_offsets     = v;
    }
    if (post) {
        if (json_find_bool(post, "\"add_prefix_space\"", &v)) bpe_model->bl_post_add_prefix_space = v;
        if (json_find_bool(post, "\"trim_offsets\"", &v))     bpe_model->bl_post_trim_offsets     = v;
    }
    if (dec) {
        if (json_find_bool(dec, "\"add_prefix_space\"", &v)) bpe_model->bl_dec_add_prefix_space = v;
        if (json_find_bool(dec, "\"trim_offsets\"", &v))     bpe_model->bl_dec_trim_offsets     = v;
    }

    free(buf);
    RTE_LOG(INFO, BPE, "ByteLevel config: pre(add_prefix_space=%d,trim_offsets=%d) post(add_prefix_space=%d,trim_offsets=%d) dec(add_prefix_space=%d,trim_offsets=%d)\n",
            (int)bpe_model->bl_pre_add_prefix_space, (int)bpe_model->bl_pre_trim_offsets,
            (int)bpe_model->bl_post_add_prefix_space, (int)bpe_model->bl_post_trim_offsets,
            (int)bpe_model->bl_dec_add_prefix_space, (int)bpe_model->bl_dec_trim_offsets);
    return 0;
}

// Load merges from tokenizer.json's "model.merges" array
int dpdk_bpe_load_merges_from_tokenizer_json(const char* filename) {
    if (!bpe_model || !filename) return -1;

    FILE* f = fopen(filename, "rb");
    if (!f) {
        RTE_LOG(ERR, BPE, "Failed to open tokenizer.json for merges: %s\n", filename);
        return -1;
    }
    const size_t MAXJ = 2 * 1024 * 1024; // up to 2MB
    char* buf = (char*)malloc(MAXJ + 1);
    if (!buf) { fclose(f); return -1; }
    size_t n = fread(buf, 1, MAXJ, f);
    fclose(f);
    buf[n] = '\0';

    // Find "model" section then the "merges" array
    const char* model = strstr(buf, "\"model\"");
    if (!model) { free(buf); RTE_LOG(ERR, BPE, "tokenizer.json: missing 'model'\n"); return -1; }
    const char* merges_key = strstr(model, "\"merges\"");
    if (!merges_key) { free(buf); RTE_LOG(ERR, BPE, "tokenizer.json: missing 'model.merges'\n"); return -1; }
    const char* p = strchr(merges_key, '[');
    if (!p) { free(buf); RTE_LOG(ERR, BPE, "tokenizer.json: 'merges' not an array\n"); return -1; }
    p++; // move past '['

    int loaded = 0;
    int rank = bpe_model->num_merges; // append after any existing merges

    // Simple JSON string reader within the array
    while (*p && *p != ']') {
        // skip whitespace and commas
        while (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r' || *p == ',') p++;
        if (*p == ']') break;
        if (*p != '"') { p++; continue; }
        p++; // past opening quote
        char entry[256];
        int ei = 0;
        while (*p && *p != '"' && ei < (int)sizeof(entry) - 1) {
            if (*p == '\\' && *(p+1) != '\0') { // handle simple escapes
                p++;
            }
            entry[ei++] = *p++;
        }
        entry[ei] = '\0';
        if (*p == '"') p++; // past closing quote

        // Expect entry like "A B" (two space-separated symbols)
        char first[MAX_TOKEN_LEN], second[MAX_TOKEN_LEN];
        first[0] = second[0] = '\0';
        if (sscanf(entry, "%127s %127s", first, second) == 2) {
            if (dpdk_bpe_add_merge(first, second, rank) == 0) {
                loaded++; rank++;
            }
        }
        // move to next potential element
        while (*p && *p != '"' && *p != ']') p++;
    }

    free(buf);
    RTE_LOG(INFO, BPE, "Loaded %d merges from tokenizer.json (%s)\n", loaded, filename);
    return loaded;
}

int dpdk_bpe_get_cache_stats(uint64_t* lookups, uint64_t* hits, uint64_t* inserts) {
    if (!bpe_model) return -1;
    if (lookups) *lookups = bpe_model->cache_lookups;
    if (hits) *hits = bpe_model->cache_hits;
    if (inserts) *inserts = bpe_model->cache_inserts;
    return 0;
}

int dpdk_bpe_get_cache_stats_ext(uint64_t* lookups, uint64_t* hits, uint64_t* inserts,
                                 uint64_t* insert_fails, uint64_t* skip_longkey,
                                 uint64_t* skip_oversize) {
    if (!bpe_model) return -1;
    if (lookups) *lookups = bpe_model->cache_lookups;
    if (hits) *hits = bpe_model->cache_hits;
    if (inserts) *inserts = bpe_model->cache_inserts;
    if (insert_fails) *insert_fails = bpe_model->cache_insert_fails;
    if (skip_longkey) *skip_longkey = bpe_model->cache_skip_longkey;
    if (skip_oversize) *skip_oversize = bpe_model->cache_skip_oversize;
    return 0;
}
int dpdk_bpe_finalize_id_merges(void) {
    if (!bpe_model || bpe_model->num_merges <= 0) return -1;
    if (bpe_model->id_merge_hash) {
        rte_hash_free(bpe_model->id_merge_hash);
        bpe_model->id_merge_hash = NULL;
    }
    if (bpe_model->id_merge_vals) {
        rte_free(bpe_model->id_merge_vals);
        bpe_model->id_merge_vals = NULL;
        bpe_model->num_id_merges = 0;
    }
    struct rte_hash_parameters hp = {
        .name = "bpe_id_merge_hash",
        .entries = (unsigned)RTE_MAX(bpe_model->num_merges, 1024),
        .key_len = sizeof(uint32_t) * 2,
        .hash_func = rte_jhash,
        .hash_func_init_val = 0,
        .socket_id = rte_socket_id(),
    };
    bpe_model->id_merge_hash = rte_hash_create(&hp);
    if (!bpe_model->id_merge_hash) {
        RTE_LOG(WARNING, BPE, "Could not create ID merge hash; keeping string-based merging\n");
        return -1;
    }
    bpe_model->id_merge_vals = rte_zmalloc_socket("bpe_id_merge_vals",
                                                  sizeof(*bpe_model->id_merge_vals) * bpe_model->num_merges,
                                                  RTE_CACHE_LINE_SIZE, rte_socket_id());
    if (!bpe_model->id_merge_vals) {
        rte_hash_free(bpe_model->id_merge_hash);
        bpe_model->id_merge_hash = NULL;
        return -1;
    }
    int added = 0;
    // Determine continuing_subword_prefix for GPT-2 (UTF-8 for U+0120 'Ġ')
    const char* cont_prefix = NULL;
    int cont_plen = 0;
    if (bpe_model->model_type == BPE_MODEL_GPT2) {
        cont_prefix = GPT2_CONT_PREFIX;
        cont_plen = GPT2_CONT_PREFIX_LEN;
    }

    for (int i = 0; i < bpe_model->num_merges; i++) {
        const char* a = bpe_model->merges[i].first;
        const char* b = bpe_model->merges[i].second;
        int a_id = dpdk_vocab_token_to_id(a);
        int b_id = dpdk_vocab_token_to_id(b);
        if (a_id < 0 || b_id < 0) continue;
        char newtok[MAX_TOKEN_LEN * 2];
        int la = (int)strnlen(a, MAX_TOKEN_LEN);
        int lb = (int)strnlen(b, MAX_TOKEN_LEN);
        // For GPT-2, the new token is a + (b without continuing_subword_prefix)
        const char* b_eff = b;
        int lb_eff = lb;
        if (cont_plen > 0 && lb >= cont_plen && strncmp(b, cont_prefix, (size_t)cont_plen) == 0) {
            b_eff = b + cont_plen;
            lb_eff = lb - cont_plen;
        }
        int copyb = RTE_MIN(lb_eff, (int)sizeof(newtok)-1 - la);
        memcpy(newtok, a, RTE_MIN(la, (int)sizeof(newtok)-1));
        if (copyb > 0) memcpy(newtok + la, b_eff, copyb);
        newtok[RTE_MIN(la + copyb, (int)sizeof(newtok)-1)] = '\0';
        int new_id = dpdk_vocab_token_to_id(newtok);
        if (new_id < 0) continue;
        id_pair_key_t key = { (uint32_t)a_id, (uint32_t)b_id };
        bpe_model->id_merge_vals[added].rank = bpe_model->merges[i].priority;
        bpe_model->id_merge_vals[added].new_id = (uint32_t)new_id;
        if (rte_hash_add_key_data(bpe_model->id_merge_hash, &key, &bpe_model->id_merge_vals[added]) >= 0) {
            added++;
        }
    }
    bpe_model->num_id_merges = added;
    RTE_LOG(INFO, BPE, "Built %d ID-based merges (of %d)\n", added, bpe_model->num_merges);
    return added > 0 ? 0 : -1;
}

void dpdk_bpe_set_produce_strings(bool enable) {
    if (bpe_model) bpe_model->produce_strings = enable;
}
