#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Simple dictionary storage
#define MAX_WORDS 1000
#define MAX_WORD_LEN 100

static char words[MAX_WORDS][MAX_WORD_LEN];
static int word_ids[MAX_WORDS];
static int word_count = 0;

int read_json_dictionary(const char* json_file) {
    FILE *json_file_ptr = fopen(json_file, "r");
    if (!json_file_ptr) {
        return -1;
    }
    
    // Read to the end of the file to get the file size.
    fseek(json_file_ptr, 0, SEEK_END);
    long file_size = ftell(json_file_ptr);

    // Read the json file from the beginning.
    fseek(json_file_ptr, 0, SEEK_SET); 
    char *json_data = malloc(file_size + 1);
    size_t bytes_read = fread(json_data, 1, file_size, json_file_ptr);
    fclose(json_file_ptr);

    json_data[file_size] = '\0';
    
    // Simple JSON parsing (assumes format: {"word": id, "word2": id2})
    char *ptr = json_data;
    word_count = 0;
    
    while (*ptr && word_count < MAX_WORDS) {
        // Find opening quote for word
        ptr = strchr(ptr, '"');
        if (!ptr) break;
        ptr++; // skip opening quote
        
        // Extract word
        char *word_start = ptr;
        ptr = strchr(ptr, '"');
        if (!ptr) break;
        
        int word_len = ptr - word_start;
        if (word_len >= MAX_WORD_LEN) word_len = MAX_WORD_LEN - 1;
        strncpy(words[word_count], word_start, word_len);
        words[word_count][word_len] = '\0';
        
        ptr++; // skip closing quote
        
        // Find colon and number
        ptr = strchr(ptr, ':');
        if (!ptr) break;
        ptr++;
        
        // Skip whitespace
        while (*ptr == ' ' || *ptr == '\t') ptr++;
        
        // Extract number
        word_ids[word_count] = atoi(ptr);
        
        word_count++;
        
        // Move to next entry
        ptr = strchr(ptr, ',');
        if (!ptr) break;
        ptr++;
    }
    
    free(json_data);
    (void)bytes_read; // Suppress unused variable warning
    return 0;
}

int lookup_token(const char *word) {
    for (int i = 0; i < word_count; i++) {
        if (strcmp(words[i], word) == 0) {
            return word_ids[i];
        }
    }
    // Return unknown token ID if word not found
    return 0;
}

