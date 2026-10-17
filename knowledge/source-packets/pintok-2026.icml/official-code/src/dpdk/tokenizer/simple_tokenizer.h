/* simple_tokenizer.h - Simple space-based tokenization */

#ifndef SIMPLE_TOKENIZER_H
#define SIMPLE_TOKENIZER_H

#ifdef __cplusplus
extern "C" {
#endif

#define SIMPLE_MAX_TOKENS 1024
#define SIMPLE_MAX_TOKEN_LEN 256

// Simple tokenizer function
int simple_tokenize(const char *text, char tokens[][SIMPLE_MAX_TOKEN_LEN], int max_tokens);

#ifdef __cplusplus
}
#endif

#endif /* SIMPLE_TOKENIZER_H */
