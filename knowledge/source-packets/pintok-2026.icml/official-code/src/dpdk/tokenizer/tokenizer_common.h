/* tokenizer_common.h - Common definitions and utilities for all tokenizers */

#ifndef TOKENIZER_COMMON_H
#define TOKENIZER_COMMON_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// Common constants
#define LISTEN_PORT    6000
#define MAX_CHUNKS     1000
#define MAX_TEXT_SIZE  (MAX_CHUNKS * 1200)
#define BUFFER_SIZE    2048

// Structure to store received chunks
struct chunk_data {
    char data[1200];
    int length;
    int received;
};

// Chunk processing state
struct chunk_processor {
    struct chunk_data chunks[MAX_CHUNKS];
    int max_chunk_received;
    int total_chunks_expected;
};

// Function to extract sequence number and total chunks from packet
void extract_chunk_header(const char *buffer, uint32_t *seq_num, uint32_t *total_chunks);

// Check if all chunks have been received
int all_chunks_received(struct chunk_processor *processor);

// Reset chunk processor for next message
void reset_chunk_processor(struct chunk_processor *processor);

// Create and bind UDP socket
int create_udp_socket(int port);

// Process a received packet and update chunk state
int process_packet(struct chunk_processor *processor, const char *buffer, int buffer_len);

#ifdef __cplusplus
}
#endif

#endif /* TOKENIZER_COMMON_H */
