#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <rte_common.h>
#include <rte_memory.h>
#include <rte_mempool.h>
#include <rte_mbuf.h>
#include <rte_log.h>
#include <rte_malloc.h>
#include <rte_hash.h>
#include <rte_jhash.h>
#include "wordpiece_util.h"

#define WP_MEMPOOL_SIZE 4096
#define WP_CACHE_SIZE 512
#define WP_HASH_ENTRIES 65536

// DPDK logging
#define RTE_LOGTYPE_WORDPIECE RTE_LOGTYPE_USER2

typedef struct {
    char token[MAX_TOKEN_LEN];
    int id;
} __rte_cache_aligned wordpiece_vocab_entry_t;

typedef struct {
    wordpiece_vocab_entry_t *vocab;
    int vocab_size;
    int unk_token_id;
    struct rte_mempool *token_pool;
    struct rte_mempool *word_pool;
    struct rte_hash *vocab_hash;
} __rte_cache_aligned wordpiece_model_t;

// Global WordPiece model instance
static wordpiece_model_t *wp_model = NULL;

/**
 * Hash function for vocabulary lookup
 */
static inline uint32_t wordpiece_hash_func(const void *key, uint32_t key_len,
                                          uint32_t init_val) {
    return rte_jhash(key, key_len, init_val);
}

/**
 * Initialize DPDK WordPiece model with memory pools and hash table
 */
int dpdk_wordpiece_init(unsigned int socket_id) {
    // Allocate model structure
    wp_model = rte_zmalloc_socket("wordpiece_model", sizeof(wordpiece_model_t),
                                  RTE_CACHE_LINE_SIZE, socket_id);
    if (!wp_model) {
        RTE_LOG(ERR, WORDPIECE, "Failed to allocate WordPiece model\n");
        return -1;
    }
    
    // Allocate vocabulary array
    wp_model->vocab = rte_zmalloc_socket("wordpiece_vocab",
                                         sizeof(wordpiece_vocab_entry_t) * MAX_VOCAB_SIZE,
                                         RTE_CACHE_LINE_SIZE, socket_id);
    if (!wp_model->vocab) {
        RTE_LOG(ERR, WORDPIECE, "Failed to allocate WordPiece vocabulary\n");
        rte_free(wp_model);
        return -1;
    }
    
    // Create memory pool for tokens
    char token_pool_name[RTE_MEMPOOL_NAMESIZE];
    snprintf(token_pool_name, sizeof(token_pool_name), "wp_token_pool_%u", socket_id);
    wp_model->token_pool = rte_mempool_create(token_pool_name,
                                              WP_MEMPOOL_SIZE,
                                              MAX_TOKEN_LEN,
                                              WP_CACHE_SIZE,
                                              0,
                                              NULL, NULL,
                                              NULL, NULL,
                                              socket_id,
                                              0);
    if (!wp_model->token_pool) {
        RTE_LOG(ERR, WORDPIECE, "Failed to create WordPiece token memory pool\n");
        rte_free(wp_model->vocab);
        rte_free(wp_model);
        return -1;
    }
    
    // Create memory pool for word processing
    char word_pool_name[RTE_MEMPOOL_NAMESIZE];
    snprintf(word_pool_name, sizeof(word_pool_name), "wp_word_pool_%u", socket_id);
    wp_model->word_pool = rte_mempool_create(word_pool_name,
                                             WP_MEMPOOL_SIZE,
                                             MAX_WORD_LEN,
                                             WP_CACHE_SIZE,
                                             0,
                                             NULL, NULL,
                                             NULL, NULL,
                                             socket_id,
                                             0);
    if (!wp_model->word_pool) {
        RTE_LOG(ERR, WORDPIECE, "Failed to create WordPiece word memory pool\n");
        rte_mempool_free(wp_model->token_pool);
        rte_free(wp_model->vocab);
        rte_free(wp_model);
        return -1;
    }
    
    // Create hash table for fast vocabulary lookup
    struct rte_hash_parameters hash_params = {
        .name = "wordpiece_vocab_hash",
        .entries = WP_HASH_ENTRIES,
        .key_len = MAX_TOKEN_LEN,
        .hash_func = wordpiece_hash_func,
        .hash_func_init_val = 0,
        .socket_id = socket_id,
    };
    
    wp_model->vocab_hash = rte_hash_create(&hash_params);
    if (!wp_model->vocab_hash) {
        RTE_LOG(ERR, WORDPIECE, "Failed to create WordPiece vocabulary hash table\n");
        rte_mempool_free(wp_model->word_pool);
        rte_mempool_free(wp_model->token_pool);
        rte_free(wp_model->vocab);
        rte_free(wp_model);
        return -1;
    }
    
    // Initialize counters
    wp_model->vocab_size = 0;
    wp_model->unk_token_id = -1;
    
    // Add unknown token
    if (dpdk_wordpiece_add_token(UNK_TOKEN) >= 0) {
        wp_model->unk_token_id = 0;
    }
    
    RTE_LOG(INFO, WORDPIECE, "DPDK WordPiece model initialized\n");
    
    return 0;
}

/**
 * Cleanup DPDK WordPiece model and free resources
 */
void dpdk_wordpiece_cleanup(void) {
    if (wp_model) {
        if (wp_model->vocab_hash) {
            rte_hash_free(wp_model->vocab_hash);
        }
        if (wp_model->word_pool) {
            rte_mempool_free(wp_model->word_pool);
        }
        if (wp_model->token_pool) {
            rte_mempool_free(wp_model->token_pool);
        }
        if (wp_model->vocab) {
            rte_free(wp_model->vocab);
        }
        rte_free(wp_model);
        wp_model = NULL;
    }
    RTE_LOG(INFO, WORDPIECE, "DPDK WordPiece model cleaned up\n");
}

/**
 * Add a token to the WordPiece vocabulary with hash table indexing
 */
int dpdk_wordpiece_add_token(const char* token) {
    if (unlikely(!wp_model)) {
        RTE_LOG(ERR, WORDPIECE, "WordPiece model not initialized\n");
        return -1;
    }
    
    if (unlikely(wp_model->vocab_size >= MAX_VOCAB_SIZE)) {
        RTE_LOG(ERR, WORDPIECE, "Maximum vocabulary size reached\n");
        return -1;
    }
    
    // Check if token already exists
    int existing_id = rte_hash_lookup(wp_model->vocab_hash, token);
    if (existing_id >= 0) {
        RTE_LOG(DEBUG, WORDPIECE, "Token '%s' already exists with ID %d\n", token, existing_id);
        return existing_id;
    }
    
    // Add new token
    wordpiece_vocab_entry_t *entry = &wp_model->vocab[wp_model->vocab_size];
    rte_strscpy(entry->token, token, MAX_TOKEN_LEN);
    entry->id = wp_model->vocab_size;
    
    // Add to hash table
    int ret = rte_hash_add_key_data(wp_model->vocab_hash, token, 
                                    (void *)(uintptr_t)wp_model->vocab_size);
    if (unlikely(ret < 0)) {
        RTE_LOG(ERR, WORDPIECE, "Failed to add token '%s' to hash table\n", token);
        return -1;
    }
    
    wp_model->vocab_size++;
    
    RTE_LOG(DEBUG, WORDPIECE, "Added token '%s' with ID %d\n", token, entry->id);
    
    return entry->id;
}

/**
 * Find token ID in vocabulary using hash table lookup
 */
static inline int dpdk_find_token_id(const char* token) {
    void *data;
    int ret = rte_hash_lookup_data(wp_model->vocab_hash, token, &data);
    if (likely(ret >= 0)) {
        return (int)(uintptr_t)data;
    }
    return -1;
}

/**
 * Check if a word can be tokenized using WordPiece algorithm with DPDK optimizations
 */
static bool dpdk_can_wordpiece_tokenize(const char* word, int word_len, 
                                        char result_tokens[][MAX_TOKEN_LEN], 
                                        int* num_tokens) {
    char temp_token[MAX_TOKEN_LEN];
    int start = 0;
    *num_tokens = 0;
    
    while (start < word_len) {
        int end = word_len;
        bool found = false;
        
        // Try to find the longest subword starting from 'start'
        // Use greedy longest-match approach
        while (start < end) {
            int substr_len = end - start;
            if (unlikely(substr_len > MAX_TOKEN_LEN - 3)) { // Account for "##" prefix
                end--;
                continue;
            }
            
            // Create token (add ## prefix if not at beginning)
            if (start == 0) {
                // First subword, no prefix
                memcpy(temp_token, word + start, substr_len);
                temp_token[substr_len] = '\0';
            } else {
                // Subsequent subwords, add ## prefix
                strcpy(temp_token, WORDPIECE_PREFIX);
                memcpy(temp_token + strlen(WORDPIECE_PREFIX), word + start, substr_len);
                temp_token[strlen(WORDPIECE_PREFIX) + substr_len] = '\0';
            }
            
            // Check if token exists in vocabulary using fast hash lookup
            if (likely(dpdk_find_token_id(temp_token) != -1)) {
                rte_strscpy(result_tokens[*num_tokens], temp_token, MAX_TOKEN_LEN);
                (*num_tokens)++;
                start = end;
                found = true;
                break;
            }
            end--;
        }
        
        if (unlikely(!found)) {
            return false; // Cannot tokenize this word
        }
    }
    
    return true;
}

/**
 * Tokenize a single word using WordPiece algorithm with DPDK optimizations
 */
static int dpdk_tokenize_word(const char* word, char tokens[][MAX_TOKEN_LEN], int max_tokens) {
    int word_len = strlen(word);
    char temp_tokens[MAX_TOKENS][MAX_TOKEN_LEN];
    int num_tokens = 0;
    
    if (unlikely(word_len == 0)) {
        return 0;
    }
    
    // Try to tokenize the word
    if (likely(dpdk_can_wordpiece_tokenize(word, word_len, temp_tokens, &num_tokens))) {
        if (unlikely(num_tokens > max_tokens)) {
            RTE_LOG(WARNING, WORDPIECE, "Word tokenization exceeded max_tokens\n");
            return -1;
        }
        
        // Copy results using optimized memory operations
        for (int i = 0; i < num_tokens; i++) {
            rte_strscpy(tokens[i], temp_tokens[i], MAX_TOKEN_LEN);
        }
        return num_tokens;
    } else {
        // If cannot tokenize, return UNK token
        if (unlikely(max_tokens < 1)) {
            return -1;
        }
        rte_strscpy(tokens[0], UNK_TOKEN, MAX_TOKEN_LEN);
        return 1;
    }
}

/**
 * Split text into words using DPDK memory pool (optimized whitespace splitting)
 */
static int dpdk_split_into_words(const char* text, char words[][MAX_TOKEN_LEN]) {
    char *temp_text;
    int ret = rte_mempool_get(wp_model->word_pool, (void **)&temp_text);
    if (unlikely(ret != 0)) {
        RTE_LOG(ERR, WORDPIECE, "Failed to get memory from word pool\n");
        return -1;
    }
    
    rte_strscpy(temp_text, text, MAX_WORD_LEN);
    
    int word_count = 0;
    char* token = strtok(temp_text, " \t\n\r\f\v");
    
    while (token != NULL && word_count < MAX_TOKENS) {
        rte_strscpy(words[word_count], token, MAX_TOKEN_LEN);
        word_count++;
        token = strtok(NULL, " \t\n\r\f\v");
    }
    
    rte_mempool_put(wp_model->word_pool, temp_text);
    
    return word_count;
}

/**
 * Perform WordPiece tokenization on input text using DPDK optimizations
 * 
 * @param text Input text to tokenize
 * @param tokens Output array to store tokens
 * @param max_tokens Maximum number of tokens to generate
 * @return Number of tokens generated, or -1 on error
 */
int dpdk_wordpiece_tokenize(const char* text, char tokens[][MAX_TOKEN_LEN], int max_tokens) {
    if (unlikely(!wp_model)) {
        RTE_LOG(ERR, WORDPIECE, "WordPiece model not initialized\n");
        return -1;
    }
    
    if (unlikely(!text || !tokens || max_tokens <= 0)) {
        RTE_LOG(ERR, WORDPIECE, "Invalid parameters for tokenization\n");
        return -1;
    }
    
    char words[MAX_TOKENS][MAX_TOKEN_LEN];
    int num_words = dpdk_split_into_words(text, words);
    
    if (unlikely(num_words == -1)) {
        return -1;
    }
    
    int total_tokens = 0;
    
    for (int i = 0; i < num_words; i++) {
        char word_tokens[MAX_TOKENS][MAX_TOKEN_LEN];
        int word_token_count = dpdk_tokenize_word(words[i], word_tokens, MAX_TOKENS);
        
        if (unlikely(word_token_count == -1)) {
            RTE_LOG(ERR, WORDPIECE, "Failed to tokenize word '%s'\n", words[i]);
            return -1;
        }
        
        // Check if we have enough space
        if (unlikely(total_tokens + word_token_count > max_tokens)) {
            RTE_LOG(ERR, WORDPIECE, "Output buffer too small for tokenization\n");
            return -1;
        }
        
        // Copy word tokens to output using optimized operations
        for (int j = 0; j < word_token_count; j++) {
            rte_strscpy(tokens[total_tokens], word_tokens[j], MAX_TOKEN_LEN);
            total_tokens++;
        }
    }
    
    RTE_LOG(DEBUG, WORDPIECE, "Tokenized '%s' into %d tokens from %d words\n",
            text, total_tokens, num_words);
    
    return total_tokens;
}

/**
 * Load WordPiece vocabulary from a file with DPDK optimizations
 * Expected format: one token per line
 */
int dpdk_wordpiece_load_vocab_from_file(const char* filename) {
    if (unlikely(!wp_model)) {
        RTE_LOG(ERR, WORDPIECE, "WordPiece model not initialized\n");
        return -1;
    }
    
    FILE* file = fopen(filename, "r");
    if (unlikely(!file)) {
        RTE_LOG(ERR, WORDPIECE, "Failed to open vocabulary file: %s\n", filename);
        return -1;
    }
    
    char line[MAX_TOKEN_LEN + 10];
    int loaded_tokens = 0;
    
    while (fgets(line, sizeof(line), file) && wp_model->vocab_size < MAX_VOCAB_SIZE) {
        // Remove newline character
        line[strcspn(line, "\n")] = '\0';
        
        if (strlen(line) > 0) {
            if (dpdk_wordpiece_add_token(line) >= 0) {
                loaded_tokens++;
            }
        }
    }
    
    fclose(file);
    
    RTE_LOG(INFO, WORDPIECE, "Loaded %d tokens from vocabulary file %s\n", 
            loaded_tokens, filename);
    
    return loaded_tokens;
}

/**
 * Get WordPiece vocabulary size
 */
int dpdk_wordpiece_get_vocab_size(void) {
    if (unlikely(!wp_model)) {
        return -1;
    }
    return wp_model->vocab_size;
}

/**
 * Get token by ID with bounds checking
 */
const char* dpdk_wordpiece_get_token_by_id(int id) {
    if (unlikely(!wp_model || id < 0 || id >= wp_model->vocab_size)) {
        return NULL;
    }
    return wp_model->vocab[id].token;
}

/**
 * Get token ID by token string using fast hash lookup
 */
int dpdk_wordpiece_get_id_by_token(const char* token) {
    if (unlikely(!wp_model || !token)) {
        return -1;
    }
    return dpdk_find_token_id(token);
}

/**
 * Get WordPiece model statistics for monitoring
 */
int dpdk_wordpiece_get_stats(struct wordpiece_stats *stats) {
    if (unlikely(!wp_model || !stats)) {
        return -1;
    }
    
    stats->vocab_size = wp_model->vocab_size;
    stats->unk_token_id = wp_model->unk_token_id;
    stats->token_pool_size = WP_MEMPOOL_SIZE;
    stats->token_pool_free = rte_mempool_avail_count(wp_model->token_pool);
    stats->word_pool_size = WP_MEMPOOL_SIZE;
    stats->word_pool_free = rte_mempool_avail_count(wp_model->word_pool);
    stats->hash_entries = rte_hash_count(wp_model->vocab_hash);
    
    return 0;
}
