/* simple_tokenizer.c - Simple space-based tokenization implementation */

#include "simple_tokenizer.h"
#include <string.h>

// Simple tokenizer function
int simple_tokenize(const char *text, char tokens[][SIMPLE_MAX_TOKEN_LEN], int max_tokens) {
    int token_count = 0;
    const char *start = text;
    const char *end = text;
    
    while (*end && token_count < max_tokens) {
        // Skip whitespace
        while (*start && (*start == ' ' || *start == '\t' || *start == '\n')) {
            start++;
        }
        
        if (!*start) break;
        
        end = start;
        // Find end of token (simple space-based splitting)
        while (*end && *end != ' ' && *end != '\t' && *end != '\n' && *end != '.' && *end != ',' && *end != '!' && *end != '?') {
            end++;
        }
        
        if (end > start) {
            int len = end - start;
            if (len >= SIMPLE_MAX_TOKEN_LEN) len = SIMPLE_MAX_TOKEN_LEN - 1; // Avoid overflow
            strncpy(tokens[token_count], start, len);
            tokens[token_count][len] = '\0';
            token_count++;
        }
        
        start = end;
    }
    
    return token_count;
}
