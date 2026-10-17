/* tokenizer_common.c - Common implementations for all tokenizers */

#include "tokenizer_common.h"

// Function to extract sequence number and total chunks from packet
void extract_chunk_header(const char *buffer, uint32_t *seq_num, uint32_t *total_chunks) {
    *seq_num = ((uint32_t)(unsigned char)buffer[0] << 24) |
               ((uint32_t)(unsigned char)buffer[1] << 16) |
               ((uint32_t)(unsigned char)buffer[2] << 8) |
               ((uint32_t)(unsigned char)buffer[3]);
               
    *total_chunks = ((uint32_t)(unsigned char)buffer[4] << 24) |
                    ((uint32_t)(unsigned char)buffer[5] << 16) |
                    ((uint32_t)(unsigned char)buffer[6] << 8) |
                    ((uint32_t)(unsigned char)buffer[7]);
}

// Check if all chunks have been received
int all_chunks_received(struct chunk_processor *processor) {
    if (processor->total_chunks_expected == 0) return 0;
    
    for (int i = 0; i < processor->total_chunks_expected; i++) {
        if (!processor->chunks[i].received) {
            return 0;
        }
    }
    return 1;
}

// Reset chunk processor for next message
void reset_chunk_processor(struct chunk_processor *processor) {
    memset(processor->chunks, 0, sizeof(processor->chunks));
    processor->max_chunk_received = -1;
    processor->total_chunks_expected = 0;
}

// Create and bind UDP socket
int create_udp_socket(int port) {
    int sockfd;
    struct sockaddr_in servaddr;

    // Create socket
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("socket creation failed");
        return -1;
    }

    memset(&servaddr, 0, sizeof(servaddr));

    // Server information
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY;
    servaddr.sin_port = htons(port);

    // Bind socket
    if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
        perror("bind failed");
        close(sockfd);
        return -1;
    }

    return sockfd;
}

// Process a received packet and update chunk state
int process_packet(struct chunk_processor *processor, const char *buffer, int buffer_len) {
    // Process payload with 8-byte header format
    if (buffer_len >= 8) {
        uint32_t seq_num, total_chunks;
        extract_chunk_header(buffer, &seq_num, &total_chunks);
        
        int text_payload_len = buffer_len - 8;
        
        fprintf(stderr, "Received chunk %u/%u, payload length: %d\n", 
               seq_num, total_chunks, text_payload_len);
        
        if (seq_num < MAX_CHUNKS && text_payload_len > 0) {
            memcpy(processor->chunks[seq_num].data, buffer + 8, text_payload_len);
            processor->chunks[seq_num].length = text_payload_len;
            processor->chunks[seq_num].received = 1;
            
            if (processor->total_chunks_expected == 0 || (int)total_chunks > processor->total_chunks_expected) {
                processor->total_chunks_expected = total_chunks;
            }
            
            if ((int)seq_num > processor->max_chunk_received) {
                processor->max_chunk_received = seq_num;
            }
            
            return 1; // Chunk processed successfully
        }
    }
    return 0; // Not a chunked message or error
}
