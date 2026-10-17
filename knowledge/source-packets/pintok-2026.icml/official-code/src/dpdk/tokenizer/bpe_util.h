#ifndef BPE_UTIL_H
#define BPE_UTIL_H

#include <rte_common.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// BPE tokenization constants
#define MAX_TOKEN_LEN 257
#define MAX_TOKENS 16384
#define MAX_MERGES 60000  // Increased to support full ModernBERT vocabulary (50,009 rules)
#define MAX_VOCAB_SIZE 60000  // Increased to support ModernBERT vocabulary (50,280 tokens)

/**
 * BPE statistics structure for monitoring
 */
struct bpe_stats {
    int vocab_size;
    int merge_count;
    int token_pool_size;
    int token_pool_free;
};

/**
 * BPE model types
 */
typedef enum {
    BPE_MODEL_MODERNBERT,  // Default ModernBERT style BPE
    BPE_MODEL_GPT2        // GPT-2 byte-level BPE with Ġ for spaces
} bpe_model_type_t;

/**
 * Initialize DPDK BPE model with memory pools
 * 
 * @param socket_id NUMA socket ID for memory allocation
 * @param model_type Type of BPE model to initialize
 * @return 0 on success, negative on error
 */
int dpdk_bpe_init(unsigned int socket_id, bpe_model_type_t model_type);

/**
 * Cleanup DPDK BPE model and free resources
 */
void dpdk_bpe_cleanup(void);

/**
 * Load tokenizer configuration from tokenizer.json file
 * 
 * @param tokenizer_json_path Path to the tokenizer.json file
 * @return 0 on success, negative on error
 */
int dpdk_bpe_load_tokenizer_config(const char* tokenizer_json_path);

/**
 * Add a merge rule to the BPE model
 * 
 * @param first First token in the merge pair
 * @param second Second token in the merge pair
 * @param priority Priority of this merge rule (higher = applied first)
 * @return 0 on success, negative on error
 */
int dpdk_bpe_add_merge(const char* first, const char* second, int priority);

/**
 * Perform BPE tokenization on input text using DPDK optimizations
 * 
 * @param text Input text to tokenize
 * @param tokens Output array to store token strings
 * @param token_ids Output array to store token IDs
 * @param max_tokens Maximum number of tokens to generate
 * @return Number of tokens generated, or -1 on error
 */
int dpdk_bpe_tokenize(const char* text, char tokens[][MAX_TOKEN_LEN], int token_ids[], int max_tokens);

/**
 * Perform BPE tokenization with token ID output using O(1) vocabulary lookup
 * 
 * @param text Input text to tokenize
 * @param tokens Output array to store token strings
 * @param token_ids Output array to store token IDs
 * @param max_tokens Maximum number of tokens to generate
 * @return Number of tokens generated, or -1 on error
 */
int dpdk_bpe_tokenize_with_ids(const char* text, char tokens[][MAX_TOKEN_LEN], 
                               int token_ids[], int max_tokens);

/**
 * Load BPE merges from a file
 * Expected format: 
 *   - ModernBERT: each line contains "first_token second_token priority"
 *   - GPT-2: each line contains "first_token second_token" (priority assigned by order)
 * 
 * @param filename Path to the merge rules file
 * @param is_gpt2_format True if file is in GPT-2 format, false for ModernBERT format
 * @return Number of merge rules loaded, or -1 on error
 */
int dpdk_bpe_load_merges_from_file(const char* filename, bool is_gpt2_format);

/**
 * Get the current vocabulary size
 * 
 * @return Vocabulary size, or -1 if model not initialized
 */
int dpdk_bpe_get_vocab_size(void);

/**
 * Get the number of loaded merge rules
 * 
 * @return Number of merge rules, or -1 if model not initialized
 */
int dpdk_bpe_get_merge_count(void);

/**
 * Get BPE model statistics for monitoring
 * 
 * @param stats Pointer to stats structure to fill
 * @return 0 on success, negative on error
 */
int dpdk_bpe_get_stats(struct bpe_stats *stats);

/**
 * Load vocabulary from file with DPDK hash table
 * Expected format:
 *   - ModernBERT: each line contains "token token_id"
 *   - GPT-2: JSON format with {"token": id, ...}
 * 
 * @param filename Path to vocabulary file
 * @param is_json_format True if file is in JSON format (GPT-2), false for line format
 * @return Number of tokens loaded, or negative on error
 */
int dpdk_bpe_load_vocab_from_file(const char* filename, bool is_json_format);

/**
 * Return a human-readable description of the last BPE error
 * Useful for surfacing initialization/load failures to callers.
 */
const char* dpdk_bpe_last_error(void);

/**
 * Load merges directly from tokenizer.json's model.merges array (GPT-2)
 */
int dpdk_bpe_load_merges_from_tokenizer_json(const char* filename);

/**
 * Get cache statistics (since model init)
 *
 * @param lookups Total cache lookup attempts
 * @param hits    Total cache hits
 * @param inserts Total cache inserts
 * @return 0 on success, negative on error
 */
int dpdk_bpe_get_cache_stats(uint64_t* lookups, uint64_t* hits, uint64_t* inserts);
// Extended cache stats (insert failures and skips)
int dpdk_bpe_get_cache_stats_ext(uint64_t* lookups, uint64_t* hits, uint64_t* inserts,
                                 uint64_t* insert_fails, uint64_t* skip_longkey,
                                 uint64_t* skip_oversize);

/**
 * Build ID-based merge map after merges and vocab are loaded
 */
int dpdk_bpe_finalize_id_merges(void);

/**
 * Control whether token strings are produced during tokenization
 * (disabling string production reduces overhead when only IDs are needed).
 */
void dpdk_bpe_set_produce_strings(bool enable);

#ifdef __cplusplus
}
#endif

#endif /* BPE_UTIL_H */
