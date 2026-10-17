#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <rte_common.h>
#include <rte_hash.h>
#include <rte_jhash.h>
#include <rte_malloc.h>
#include <rte_log.h>
#include <rte_string_fns.h>
#include "vocab_util.h"

#define RTE_LOGTYPE_VOCAB RTE_LOGTYPE_USER2

// Use a fixed-width key for the hash table. DPDK hash supports keys up to 256 bytes reliably.
// GPT-2 tokens are at most 256 bytes, so 256 covers all tokens while avoiding oversized keys.
typedef struct {
    char s[256];
} token_key_t;

// Global vocabulary table
static vocab_table_t *vocab_table = NULL;

/**
 * Initialize DPDK vocabulary system with hash table
 */
int dpdk_vocab_init(unsigned int socket_id) {
    // Allocate vocabulary table structure
    vocab_table = rte_zmalloc_socket("vocab_table", sizeof(vocab_table_t),
                                     RTE_CACHE_LINE_SIZE, socket_id);
    if (!vocab_table) {
        RTE_LOG(ERR, VOCAB, "Failed to allocate vocabulary table\n");
        return -1;
    }
    
    // Configure hash table parameters for O(1) token→ID lookup
    char hash_name[RTE_HASH_NAMESIZE];
    snprintf(hash_name, sizeof(hash_name), "vocab_hash_%u", socket_id);
    
    struct rte_hash_parameters hash_params = {
        .name = hash_name,
        .entries = MAX_VOCAB_SIZE * 1.2,  // 20% extra for efficiency
        .key_len = sizeof(token_key_t),
        .hash_func = rte_jhash,           // Fast Jenkins hash
        .hash_func_init_val = 0,
        .socket_id = socket_id,
        .extra_flag = RTE_HASH_EXTRA_FLAGS_RW_CONCURRENCY  // Allow concurrent reads
    };
    
    vocab_table->token_to_id_hash = rte_hash_create(&hash_params);
    if (!vocab_table->token_to_id_hash) {
        RTE_LOG(ERR, VOCAB, "Failed to create vocabulary hash table\n");
        rte_free(vocab_table);
        vocab_table = NULL;
        return -1;
    }
    
    // Allocate ID→token array for O(1) reverse lookup
    vocab_table->id_to_token_array = rte_zmalloc_socket("vocab_id_to_token",
                                                        sizeof(vocab_entry_t) * MAX_VOCAB_SIZE,
                                                        RTE_CACHE_LINE_SIZE, socket_id);
    if (!vocab_table->id_to_token_array) {
        RTE_LOG(ERR, VOCAB, "Failed to allocate ID→token array\n");
        rte_hash_free(vocab_table->token_to_id_hash);
        rte_free(vocab_table);
        vocab_table = NULL;
        return -1;
    }
    
    vocab_table->vocab_size = 0;
    vocab_table->max_token_id = -1;
    strcpy(vocab_table->vocab_name, "unknown");
    
    RTE_LOG(INFO, VOCAB, "DPDK vocabulary system initialized\n");
    
    return 0;
}

/**
 * Cleanup vocabulary system and free resources
 */
void dpdk_vocab_cleanup(void) {
    if (vocab_table) {
        if (vocab_table->token_to_id_hash) {
            rte_hash_free(vocab_table->token_to_id_hash);
        }
        if (vocab_table->id_to_token_array) {
            rte_free(vocab_table->id_to_token_array);
        }
        rte_free(vocab_table);
        vocab_table = NULL;
    }
    RTE_LOG(INFO, VOCAB, "DPDK vocabulary system cleaned up\n");
}

/**
 * Add a token to the vocabulary with O(1) hash table insertion
 */
static int dpdk_vocab_add_token(const char* token, int token_id) {
    if (!vocab_table || !token) {
        return -1;
    }
    
    if (vocab_table->vocab_size >= MAX_VOCAB_SIZE) {
        RTE_LOG(ERR, VOCAB, "Vocabulary size limit exceeded\n");
        return -1;
    }
    
    if (token_id < 0 || token_id >= MAX_VOCAB_SIZE) {
        RTE_LOG(ERR, VOCAB, "Invalid token ID: %d\n", token_id);
        return -1;
    }

    // Build canonical zero-padded key (fixed width)
    token_key_t key;
    memset(&key, 0, sizeof(key));
    rte_strscpy(key.s, token, sizeof(key.s));

    // Add to hash table for token→ID lookup
    int ret = rte_hash_add_key_data(vocab_table->token_to_id_hash,
                                    &key, (void*)(intptr_t)token_id);
    if (ret < 0) {
        printf("Failed to add token '%s' to hash table: %d\n", token, ret);
        return -1;
    }

    // Add to array for ID→token lookup
    if (token_id >= MAX_VOCAB_SIZE) {
        RTE_LOG(ERR, VOCAB, "Token ID %d exceeds array size\n", token_id);
        return -1;
    }
    
    rte_strscpy(vocab_table->id_to_token_array[token_id].token, token, MAX_TOKEN_LEN);
    vocab_table->id_to_token_array[token_id].token_id = token_id;
    
    vocab_table->vocab_size++;
    if (token_id > vocab_table->max_token_id) {
        vocab_table->max_token_id = token_id;
    }
    
    return 0;
}

/**
 * Load vocabulary from DPDK-format file
 * Expected format: "token token_id" per line
 */
int dpdk_vocab_load_from_file(const char* vocab_file) {
    if (!vocab_table) {
        printf("Vocabulary system not initialized\n");
        return -1;
    }
    
    FILE* file = fopen(vocab_file, "rb");
    if (!file) {
        printf("Failed to open vocabulary file: %s\n", vocab_file);
        return -1;
    }
    
    char line[512];
    char token[MAX_TOKEN_LEN];
    int token_id;
    int loaded_tokens = 0;
    int line_num = 0;
    
    while (fgets(line, sizeof(line), file)) {
        line_num++;
        
        // Skip comments and empty lines
        if (line[0] == '#' || line[0] == '\n' || line[0] == '\0') {
            continue;
        }
        
        // Parse: token token_id (handle tokens with whitespace)
        // Find the last space in the line to separate token from ID
        char* trimmed_line = line;
        while (*trimmed_line && isspace(*trimmed_line)) trimmed_line++; // Skip leading whitespace
        
        // Remove trailing newline
        char* newline = strchr(trimmed_line, '\n');
        if (newline) *newline = '\0';
        
        // Find the last space to separate token from ID
        char* last_space = strrchr(trimmed_line, ' ');
        if (last_space && sscanf(last_space + 1, "%d", &token_id) == 1) {
            // Extract token (everything before the last space)
            size_t token_len = last_space - trimmed_line;
            if (token_len < sizeof(token)) {
                memset(token, 0, sizeof(token));  // Zero-initialize the entire buffer
                strncpy(token, trimmed_line, token_len);
                token[token_len] = '\0';
                
                if (dpdk_vocab_add_token(token, token_id) == 0) {
                    loaded_tokens++;
                } else {
                    printf("WARNING: Failed to add token at line %d: %s\n", line_num, line);
                }
            } else {
                printf("WARNING: Token too long at line %d: %s\n", line_num, line);
            }
        } else {
            printf("WARNING: Invalid format at line %d: %s\n", line_num, line);
        }
    }
    
    fclose(file);
    
    // Extract model name from filename
    const char* filename = strrchr(vocab_file, '/');
    if (filename) {
        filename++;  // Skip the '/'
    } else {
        filename = vocab_file;
    }
    rte_strlcpy(vocab_table->vocab_name, filename, sizeof(vocab_table->vocab_name));
    
    RTE_LOG(INFO, VOCAB, "Loaded %d tokens from %s (max ID: %d)\n", 
            loaded_tokens, vocab_file, vocab_table->max_token_id);
    
    return loaded_tokens;
}

/**
 * Load vocabulary from JSON file (GPT-2 format)
 * Expected format: {"token1": id1, "token2": id2, ...}
 */
int dpdk_vocab_load_from_json(const char* vocab_file) {
    if (unlikely(!vocab_table)) {
        RTE_LOG(ERR, VOCAB, "Vocabulary system not initialized\n");
        return -1;
    }
    
    FILE* file = fopen(vocab_file, "rb");
    if (unlikely(!file)) {
        RTE_LOG(ERR, VOCAB, "Failed to open vocabulary file: %s\n", vocab_file);
        return -1;
    }
    
    // Read entire file into buffer
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    char* json_buffer = rte_malloc("json_buffer", file_size + 1, 0);
    if (!json_buffer) {
        fclose(file);
        return -1;
    }
    
    size_t read_size = fread(json_buffer, 1, file_size, file);
    json_buffer[read_size] = '\0';
    fclose(file);
    
    // Simple JSON parsing (assumes format: {"token": id, ...})
    int loaded_tokens = 0;
    char* ptr = json_buffer;
    char token[MAX_TOKEN_LEN];
    int token_id;
    
    while (*ptr) {
        // Skip whitespace and find opening quote
        while (*ptr && (*ptr == ' ' || *ptr == '\n' || *ptr == '\t' || *ptr == '{' || *ptr == ',')) ptr++;
        if (*ptr == '}') break;
        if (*ptr != '"') { ptr++; continue; }
        
        // Parse token
        ptr++; // Skip opening quote
        int i = 0;
        while (*ptr && *ptr != '"' && i < MAX_TOKEN_LEN - 1) {
            if (*ptr == '\\' && *(ptr + 1)) {
                // Handle escape sequences (including \uXXXX)
                ptr++;
                if (*ptr == 'n') { token[i++] = '\n'; ptr++; }
                else if (*ptr == 't') { token[i++] = '\t'; ptr++; }
                else if (*ptr == 'r') { token[i++] = '\r'; ptr++; }
                else if (*ptr == '"') { token[i++] = '"'; ptr++; }
                else if (*ptr == '\\') { token[i++] = '\\'; ptr++; }
                else if (*ptr == 'u' && isxdigit((unsigned char)ptr[1]) && isxdigit((unsigned char)ptr[2]) && isxdigit((unsigned char)ptr[3]) && isxdigit((unsigned char)ptr[4])) {
                    // Decode \uXXXX -> UTF-8
                    int h1 = isdigit((unsigned char)ptr[1]) ? ptr[1]-'0' : (tolower((unsigned char)ptr[1])-'a'+10);
                    int h2 = isdigit((unsigned char)ptr[2]) ? ptr[2]-'0' : (tolower((unsigned char)ptr[2])-'a'+10);
                    int h3 = isdigit((unsigned char)ptr[3]) ? ptr[3]-'0' : (tolower((unsigned char)ptr[3])-'a'+10);
                    int h4 = isdigit((unsigned char)ptr[4]) ? ptr[4]-'0' : (tolower((unsigned char)ptr[4])-'a'+10);
                    unsigned int cp = (unsigned int)((h1<<12) | (h2<<8) | (h3<<4) | h4);
                    if (cp <= 0x7F) {
                        if (i + 1 < MAX_TOKEN_LEN) token[i++] = (char)cp;
                    } else if (cp <= 0x7FF) {
                        if (i + 2 < MAX_TOKEN_LEN) {
                            token[i++] = (char)(0xC0 | (cp >> 6));
                            token[i++] = (char)(0x80 | (cp & 0x3F));
                        }
                    } else {
                        if (i + 3 < MAX_TOKEN_LEN) {
                            token[i++] = (char)(0xE0 | (cp >> 12));
                            token[i++] = (char)(0x80 | ((cp >> 6) & 0x3F));
                            token[i++] = (char)(0x80 | (cp & 0x3F));
                        }
                    }
                    ptr += 5; // consumed 'u' + 4 hex digits
                } else {
                    // Unknown escape, copy as-is
                    token[i++] = *ptr;
                    if (*ptr) ptr++;
                }
            } else {
                token[i++] = *ptr++;
            }
        }
        token[i] = '\0';
        
        if (*ptr == '"') ptr++; // Skip closing quote
        
        // Skip to colon
        while (*ptr && *ptr != ':') ptr++;
        if (*ptr == ':') ptr++;
        
        // Parse token ID
        while (*ptr && (*ptr == ' ' || *ptr == '\t')) ptr++;
        if (sscanf(ptr, "%d", &token_id) == 1) {
            // Add to vocabulary
            if (loaded_tokens < MAX_VOCAB_SIZE) {
                rte_strscpy(vocab_table->id_to_token_array[token_id].token, token, MAX_TOKEN_LEN);
                vocab_table->id_to_token_array[token_id].token_id = token_id;
                
                // Create key for hash table (zero-padded, fixed width)
                token_key_t key;
                memset(&key, 0, sizeof(key));
                rte_strscpy(key.s, token, sizeof(key.s));
                
                // Add to hash table for O(1) lookup
                int ret = rte_hash_add_key_data(vocab_table->token_to_id_hash, 
                                               &key, (void*)(intptr_t)token_id);
                if (ret < 0) {
                    printf("WARNING: Failed to add token '%s' to hash table\n", token);
                }

                loaded_tokens++;
                vocab_table->vocab_size++;
                if (token_id > vocab_table->max_token_id) {
                    vocab_table->max_token_id = token_id;
                }
            }
        }
        
        // Skip to next entry
        while (*ptr && *ptr != ',' && *ptr != '}') ptr++;
    }
    
    rte_free(json_buffer);
    
    // Store vocabulary name
    const char* filename = strrchr(vocab_file, '/');
    if (filename) {
        filename++;
    } else {
        filename = vocab_file;
    }
    rte_strscpy(vocab_table->vocab_name, filename, sizeof(vocab_table->vocab_name));
    
    RTE_LOG(INFO, VOCAB, "Loaded %d tokens from JSON %s (max ID: %d)\n", 
            loaded_tokens, vocab_file, vocab_table->max_token_id);
    
    return loaded_tokens;
}

/**
 * O(1) token to ID lookup using hash table
 */
int dpdk_vocab_token_to_id(const char* token) {
    if (unlikely(!vocab_table || !token)) {
        return -1;
    }

    // Ensure key is zero-padded for consistent hash lookup
    token_key_t key;
    memset(&key, 0, sizeof(key));
    rte_strscpy(key.s, token, sizeof(key.s));

    void* data = NULL;
    int ret = rte_hash_lookup_data(vocab_table->token_to_id_hash, &key, &data);
    if (likely(ret >= 0)) {
        return (int)(intptr_t)data;
    }
    // Token not found
    return -1;
}

/**
 * O(1) ID to token lookup using array
 */
const char* dpdk_vocab_id_to_token(int token_id) {
    if (unlikely(!vocab_table || token_id < 0 || token_id > vocab_table->max_token_id)) {
        return "<unk>";
    }
    
    return vocab_table->id_to_token_array[token_id].token;
}

/**
 * Get vocabulary size
 */
int dpdk_vocab_get_size(void) {
    if (unlikely(!vocab_table)) {
        return -1;
    }
    return vocab_table->vocab_size;
}

/**
 * Print vocabulary statistics
 */
void dpdk_vocab_print_stats(void) {
    if (!vocab_table) {
        RTE_LOG(INFO, VOCAB, "Vocabulary system not initialized\n");
        return;
    }
    
    RTE_LOG(INFO, VOCAB, "Vocabulary Statistics:\n");
    RTE_LOG(INFO, VOCAB, "  Model: %s\n", vocab_table->vocab_name);
    RTE_LOG(INFO, VOCAB, "  Total tokens: %d\n", vocab_table->vocab_size);
    RTE_LOG(INFO, VOCAB, "  Max token ID: %d\n", vocab_table->max_token_id);
    RTE_LOG(INFO, VOCAB, "  Hash table entries: %u\n", 
            rte_hash_count(vocab_table->token_to_id_hash));
}
