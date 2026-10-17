#ifndef WORDPIECE_UTIL_H
#define WORDPIECE_UTIL_H

#include <rte_common.h>

#ifdef __cplusplus
extern "C" {
#endif

// WordPiece tokenization constants
#define MAX_TOKEN_LEN 128
#define MAX_TOKENS 1024
#define MAX_VOCAB_SIZE 50000
#define MAX_WORD_LEN 256
#define WORDPIECE_PREFIX "##"
#define UNK_TOKEN "[UNK]"

/**
 * WordPiece statistics structure for monitoring
 */
struct wordpiece_stats {
    int vocab_size;
    int unk_token_id;
    int token_pool_size;
    int token_pool_free;
    int word_pool_size;
    int word_pool_free;
    int hash_entries;
};

/**
 * Initialize DPDK WordPiece model with memory pools and hash table
 * 
 * @param socket_id NUMA socket ID for memory allocation
 * @return 0 on success, negative on error
 */
int dpdk_wordpiece_init(unsigned int socket_id);

/**
 * Cleanup DPDK WordPiece model and free resources
 */
void dpdk_wordpiece_cleanup(void);

/**
 * Add a token to the WordPiece vocabulary
 * 
 * @param token Token string to add to vocabulary
 * @return Token ID on success, negative on error
 */
int dpdk_wordpiece_add_token(const char* token);

/**
 * Perform WordPiece tokenization on input text using DPDK optimizations
 * 
 * @param text Input text to tokenize
 * @param tokens Output array to store tokens
 * @param max_tokens Maximum number of tokens to generate
 * @return Number of tokens generated, or -1 on error
 */
int dpdk_wordpiece_tokenize(const char* text, char tokens[][MAX_TOKEN_LEN], int max_tokens);

/**
 * Load WordPiece vocabulary from a file
 * Expected format: one token per line
 * 
 * @param filename Path to the vocabulary file
 * @return Number of tokens loaded, or -1 on error
 */
int dpdk_wordpiece_load_vocab_from_file(const char* filename);

/**
 * Get the current vocabulary size
 * 
 * @return Vocabulary size, or -1 if model not initialized
 */
int dpdk_wordpiece_get_vocab_size(void);

/**
 * Get token string by ID
 * 
 * @param id Token ID
 * @return Token string, or NULL if not found
 */
const char* dpdk_wordpiece_get_token_by_id(int id);

/**
 * Get token ID by token string
 * 
 * @param token Token string
 * @return Token ID, or -1 if not found
 */
int dpdk_wordpiece_get_id_by_token(const char* token);

/**
 * Get WordPiece model statistics for monitoring
 * 
 * @param stats Pointer to stats structure to fill
 * @return 0 on success, negative on error
 */
int dpdk_wordpiece_get_stats(struct wordpiece_stats *stats);

#ifdef __cplusplus
}
#endif

#endif /* WORDPIECE_UTIL_H */
