#ifndef VOCAB_UTIL_H
#define VOCAB_UTIL_H

#include <rte_hash.h>
#include <rte_malloc.h>
#include "bpe_util.h"  // For MAX_TOKEN_LEN and MAX_VOCAB_SIZE

#define UNK_TOKEN_ID -1  // Usually <unk> token
#define PAD_TOKEN_ID 1  // Usually <pad> token

typedef struct {
    char token[MAX_TOKEN_LEN];
    int token_id;
} __rte_cache_aligned vocab_entry_t;

typedef struct {
    struct rte_hash *token_to_id_hash;  // O(1) token→ID lookup
    vocab_entry_t *id_to_token_array;   // O(1) ID→token lookup  
    int vocab_size;
    int max_token_id;
    char vocab_name[64];
} __rte_cache_aligned vocab_table_t;

// Vocabulary management functions
int dpdk_vocab_init(unsigned int socket_id);
void dpdk_vocab_cleanup(void);
int dpdk_vocab_load_from_file(const char* vocab_file);
int dpdk_vocab_load_from_json(const char* vocab_file);  // For GPT-2 JSON format

// O(1) lookup functions
int dpdk_vocab_token_to_id(const char* token);
const char* dpdk_vocab_id_to_token(int token_id);

// Statistics
int dpdk_vocab_get_size(void);
void dpdk_vocab_print_stats(void);

#endif // VOCAB_UTIL_H
