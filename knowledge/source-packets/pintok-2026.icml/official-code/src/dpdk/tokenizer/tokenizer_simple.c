/* tokenizer_simple.c - Basic simple tokenizer (no DPDK) */

#include <time.h>
#include <sys/time.h>
#include "tokenizer_common.h"
#include "simple_tokenizer.h"
#include "output_utils.h"

// Get high resolution timestamp (fallback when no TSC available)
static uint64_t get_timestamp_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000 + ts.tv_nsec / 1000;
}

// Process complete message when all chunks are received
void process_complete_message(struct chunk_processor *processor, uint64_t first_packet_arrival) {
    // Concatenate all chunks
    char complete_text[MAX_TEXT_SIZE] = {0};
    int total_length = 0;
    
    for (int i = 0; i < processor->total_chunks_expected && total_length < MAX_TEXT_SIZE - 1; i++) {
        if (processor->chunks[i].received) {
            int copy_len = processor->chunks[i].length;
            if (total_length + copy_len >= MAX_TEXT_SIZE) {
                copy_len = MAX_TEXT_SIZE - total_length - 1;
            }
            memcpy(complete_text + total_length, processor->chunks[i].data, copy_len);
            total_length += copy_len;
        }
    }
    complete_text[total_length] = '\0';
    
    // Tokenize using simple tokenizer
    char tokens[SIMPLE_MAX_TOKENS][SIMPLE_MAX_TOKEN_LEN];
    int num_tokens = simple_tokenize(complete_text, tokens, SIMPLE_MAX_TOKENS);
    
    uint64_t tokenize_end = get_timestamp_us();
    
    // Convert tokens to standard format and create token IDs
    char output_tokens[SIMPLE_MAX_TOKENS][256];
    int token_ids[SIMPLE_MAX_TOKENS];
    for (int i = 0; i < num_tokens; i++) {
        strncpy(output_tokens[i], tokens[i], 255);
        output_tokens[i][255] = '\0';
        token_ids[i] = i; // Simple sequential IDs
    }
    
    // Output results
    output_tokenization_results(
        "SIMPLE",
        first_packet_arrival,
        tokenize_end,
        1000000, // 1MHz fake frequency for microsecond timestamps
        complete_text,
        num_tokens,
        output_tokens,
        token_ids
    );
    
    print_latency("SIMPLE", first_packet_arrival, tokenize_end, 1000000);
    
    // Reset for next message
    reset_chunk_processor(processor);
}

int main(void) {
    struct chunk_processor processor = {0};
    char buffer[BUFFER_SIZE];
    struct sockaddr_in cliaddr;
    socklen_t len = sizeof(cliaddr);
    
    // Create and bind socket
    int sockfd = create_udp_socket(LISTEN_PORT);
    if (sockfd < 0) {
        exit(EXIT_FAILURE);
    }

    fprintf(stderr, "Simple tokenizer listening on UDP port %d\n", LISTEN_PORT);
    fprintf(stderr, "Using microsecond timing\n");

    // Main packet processing loop
    while (1) {
        int n = recvfrom(sockfd, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&cliaddr, &len);
        if (n > 0) {
            uint64_t packet_arrival = get_timestamp_us();
            
            if (process_packet(&processor, buffer, n)) {
                // Check if we have all chunks
                if (all_chunks_received(&processor)) {
                    process_complete_message(&processor, packet_arrival);
                }
            } else {
                // Handle as plain text for backward compatibility
                buffer[n] = '\0';
                
                fprintf(stderr, "Received plain text: %s\n", buffer);
                
                // Tokenize using simple tokenizer
                char tokens[SIMPLE_MAX_TOKENS][SIMPLE_MAX_TOKEN_LEN];
                int num_tokens = simple_tokenize(buffer, tokens, SIMPLE_MAX_TOKENS);
                
                uint64_t tokenize_end = get_timestamp_us();
                
                // Convert to standard format
                char output_tokens[SIMPLE_MAX_TOKENS][256];
                int token_ids[SIMPLE_MAX_TOKENS];
                for (int i = 0; i < num_tokens; i++) {
                    strncpy(output_tokens[i], tokens[i], 255);
                    output_tokens[i][255] = '\0';
                    token_ids[i] = i;
                }
                
                output_tokenization_results(
                    "SIMPLE",
                    packet_arrival,
                    tokenize_end,
                    1000000,
                    buffer,
                    num_tokens,
                    output_tokens,
                    token_ids
                );
                
                print_latency("SIMPLE", packet_arrival, tokenize_end, 1000000);
            }
        }
    }

    close(sockfd);
    return EXIT_SUCCESS;
}
