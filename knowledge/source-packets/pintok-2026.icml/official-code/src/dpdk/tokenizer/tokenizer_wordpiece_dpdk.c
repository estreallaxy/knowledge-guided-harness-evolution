// tokenizer_wordpiece_dpdk.c - DPDK-based WordPiece tokenizer for comparison

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_mbuf.h>
#include <rte_ether.h>
#include <rte_ip.h>
#include <rte_udp.h>
#include <rte_mempool.h>
#include <rte_cycles.h>
#include "wordpiece_util.h"

#define PORT_ID        0
#define RX_QUEUE_ID    0
#define TX_QUEUE_ID    0
#define BURST_SIZE     32
#define LISTEN_PORT    6000
#define NUM_MBUFS      8191
#define MBUF_CACHE_SIZE 250
#define MAX_CHUNKS     1000
#define MAX_TEXT_SIZE  (MAX_CHUNKS * 1200)

// Structure to store received chunks
struct chunk_data {
    char data[1200];
    int length;
    int received;
};

static struct chunk_data chunks[MAX_CHUNKS];
static int max_chunk_received = -1;
static int total_chunks_expected = 0;
static uint64_t tsc_hz = 0;

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

// Function to process complete message using WordPiece
void process_complete_message(uint64_t packet_arrival_time) {
    uint64_t start_cycles = rte_rdtsc();
    
    char *complete_text = malloc(MAX_TEXT_SIZE);
    int total_length = 0;
    
    // Reassemble chunks in order
    for (int i = 0; i <= max_chunk_received; i++) {
        if (chunks[i].received) {
            memcpy(complete_text + total_length, chunks[i].data, chunks[i].length);
            total_length += chunks[i].length;
        }
    }
    complete_text[total_length] = '\0';
    
    uint64_t assembly_cycles = rte_rdtsc();
    
    // Tokenize using WordPiece
    char tokens[MAX_TOKENS][MAX_TOKEN_LEN];
    int num_tokens = dpdk_wordpiece_tokenize(complete_text, tokens, MAX_TOKENS);
    
    uint64_t tokenize_cycles = rte_rdtsc();
    
    // Output results in a structured format for Python parsing
    printf("DPDK_TOKENIZATION_START\n");
    printf("PACKET_ARRIVAL_TIME: %lu\n", packet_arrival_time);
    printf("ASSEMBLY_START_TIME: %lu\n", start_cycles);
    printf("TOKENIZE_START_TIME: %lu\n", assembly_cycles);
    printf("TOKENIZE_END_TIME: %lu\n", tokenize_cycles);
    printf("TSC_FREQUENCY: %lu\n", tsc_hz);
    printf("ORIGINAL_TEXT: %s\n", complete_text);
    printf("NUM_TOKENS: %d\n", num_tokens);
    printf("TOKENS: ");
    for (int i = 0; i < num_tokens; i++) {
        printf("%s", tokens[i]);
        if (i < num_tokens - 1) printf(" ");
    }
    printf("\n");
    printf("TOKEN_IDS: ");
    for (int i = 0; i < num_tokens; i++) {
        int token_id = dpdk_wordpiece_get_id_by_token(tokens[i]);
        printf("%d", token_id);
        if (i < num_tokens - 1) printf(" ");
    }
    printf("\n");
    printf("DPDK_TOKENIZATION_END\n");
    fflush(stdout);
    
    // Calculate and report latencies
    double total_latency_us = (double)(tokenize_cycles - packet_arrival_time) * 1000000.0 / tsc_hz;
    double assembly_latency_us = (double)(assembly_cycles - start_cycles) * 1000000.0 / tsc_hz;
    double tokenize_latency_us = (double)(tokenize_cycles - assembly_cycles) * 1000000.0 / tsc_hz;
    
    fprintf(stderr, "DPDK_LATENCY_BREAKDOWN: total=%.2f assembly=%.2f tokenize=%.2f us\n",
           total_latency_us, assembly_latency_us, tokenize_latency_us);
    
    // Reset for next message
    memset(chunks, 0, sizeof(chunks));
    max_chunk_received = -1;
    total_chunks_expected = 0;
    
    free(complete_text);
}

// Function to check if all chunks are received
int all_chunks_received() {
    if (total_chunks_expected <= 0) {
        return 0;
    }
    
    for (int i = 0; i < total_chunks_expected; i++) {
        if (!chunks[i].received) {
            return 0;
        }
    }
    return 1;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <vocab.txt> [DPDK EAL args...]\n", argv[0]);
        return EXIT_FAILURE;
    }
    const char *vocab_file = argv[1];

    // Initialize DPDK EAL
    int ret = rte_eal_init(argc, argv);
    if (ret < 0)
        rte_exit(EXIT_FAILURE, "Failed to initialize DPDK EAL\n");

    // Initialize TSC frequency
    tsc_hz = rte_get_tsc_hz();
    fprintf(stderr, "TSC frequency: %lu Hz\n", tsc_hz);

    // Initialize WordPiece model
    if (dpdk_wordpiece_init(0) != 0) {
        rte_exit(EXIT_FAILURE, "Failed to initialize WordPiece model\n");
    }

    // Load vocabulary
    int vocab_size = dpdk_wordpiece_load_vocab_from_file(vocab_file);
    if (vocab_size < 0) {
        rte_exit(EXIT_FAILURE, "Failed to load vocabulary from '%s'\n", vocab_file);
    }
    fprintf(stderr, "Loaded vocabulary: %d tokens\n", vocab_size);

    // Check if we have any ports
    uint16_t nb_ports = rte_eth_dev_count_avail();
    if (nb_ports == 0)
        rte_exit(EXIT_FAILURE, "No Ethernet ports - bye\n");

    // Create mbuf pool
    struct rte_mempool *mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", NUM_MBUFS,
        MBUF_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE, rte_socket_id());
    if (mbuf_pool == NULL)
        rte_exit(EXIT_FAILURE, "Cannot create mbuf pool\n");

    // Configure the Ethernet device
    struct rte_eth_conf port_conf = {0};
    port_conf.rxmode.mq_mode = RTE_ETH_MQ_RX_NONE;
    
    if (rte_eth_dev_configure(PORT_ID, 1, 1, &port_conf) < 0)
        rte_exit(EXIT_FAILURE, "Cannot configure port %u\n", PORT_ID);

    // Set up RX queue
    if (rte_eth_rx_queue_setup(PORT_ID, RX_QUEUE_ID, 128,
                               rte_eth_dev_socket_id(PORT_ID),
                               NULL, mbuf_pool) < 0)
        rte_exit(EXIT_FAILURE, "RX queue setup failed\n");

    // Set up TX queue  
    if (rte_eth_tx_queue_setup(PORT_ID, TX_QUEUE_ID, 512,
                               rte_eth_dev_socket_id(PORT_ID),
                               NULL) < 0)
        rte_exit(EXIT_FAILURE, "TX queue setup failed\n");

    // Start the Ethernet port
    if (rte_eth_dev_start(PORT_ID) < 0)
        rte_exit(EXIT_FAILURE, "Cannot start port %u\n", PORT_ID);

    // Enable promiscuous mode
    if (rte_eth_promiscuous_enable(PORT_ID) != 0)
        rte_exit(EXIT_FAILURE, "Cannot enable promiscuous mode\n");

    struct rte_eth_link link;
    int ret_link = rte_eth_link_get_nowait(PORT_ID, &link);
    if (ret_link != 0) {
        fprintf(stderr, "Warning: Could not get link status\n");
    }
    
    fprintf(stderr, "DPDK WordPiece tokenizer initialized successfully\n");
    fprintf(stderr, "Port %u: Link %s, Speed %u Mbps\n", PORT_ID,
           link.link_status ? "UP" : "DOWN", link.link_speed);
    fprintf(stderr, "Listening for UDP packets on port %u\n", LISTEN_PORT);

    // Main packet processing loop
    struct rte_mbuf *bufs[BURST_SIZE];
    unsigned long total_packets = 0;
    
    while (1) {
        uint16_t nb_rx = rte_eth_rx_burst(PORT_ID, RX_QUEUE_ID, bufs, BURST_SIZE);
        if (nb_rx == 0)
            continue;
            
        total_packets += nb_rx;
        
        for (uint16_t i = 0; i < nb_rx; ++i) {
            struct rte_mbuf *m = bufs[i];
            
            // Record packet arrival time as early as possible
            uint64_t packet_arrival_cycles = rte_rdtsc();
            
            // Get packet data
            unsigned char *pkt_data = rte_pktmbuf_mtod(m, unsigned char *);
            uint16_t pkt_len = rte_pktmbuf_data_len(m);
            
            // Parse Ethernet header
            if (pkt_len < sizeof(struct rte_ether_hdr)) {
                rte_pktmbuf_free(m);
                continue;
            }
            
            struct rte_ether_hdr *eth_hdr = (struct rte_ether_hdr *)pkt_data;
            if (eth_hdr->ether_type != rte_cpu_to_be_16(RTE_ETHER_TYPE_IPV4)) {
                rte_pktmbuf_free(m);
                continue;
            }

            // Parse IPv4 header
            struct rte_ipv4_hdr *ip_hdr = (struct rte_ipv4_hdr *)(pkt_data + sizeof(struct rte_ether_hdr));
            if (pkt_len < sizeof(struct rte_ether_hdr) + sizeof(struct rte_ipv4_hdr) ||
                ip_hdr->next_proto_id != IPPROTO_UDP) {
                rte_pktmbuf_free(m);
                continue;
            }

            // Parse UDP header
            uint16_t ip_hdr_len = (ip_hdr->version_ihl & 0x0f) * 4;
            struct rte_udp_hdr *udp_hdr = (struct rte_udp_hdr *)(pkt_data + sizeof(struct rte_ether_hdr) + ip_hdr_len);
            
            if (pkt_len < sizeof(struct rte_ether_hdr) + ip_hdr_len + sizeof(struct rte_udp_hdr)) {
                rte_pktmbuf_free(m);
                continue;
            }
            
            // Check if this is our target port
            if (rte_be_to_cpu_16(udp_hdr->dst_port) != LISTEN_PORT) {
                rte_pktmbuf_free(m);
                continue;
            }

            // Extract UDP payload
            uint16_t udp_payload_len = rte_be_to_cpu_16(udp_hdr->dgram_len) - sizeof(struct rte_udp_hdr);
            char *payload = (char *)(pkt_data + sizeof(struct rte_ether_hdr) + ip_hdr_len + sizeof(struct rte_udp_hdr));
            
            if (udp_payload_len <= 0) {
                rte_pktmbuf_free(m);
                continue;
            }
            
            // Process payload with 8-byte header format
            if (udp_payload_len >= 8) {
                uint32_t seq_num, total_chunks;
                extract_chunk_header(payload, &seq_num, &total_chunks);
                
                int text_payload_len = udp_payload_len - 8;
                
                fprintf(stderr, "Received chunk %u/%u, payload length: %d\n", 
                       seq_num, total_chunks, text_payload_len);
                
                if (seq_num < MAX_CHUNKS && text_payload_len > 0) {
                    memcpy(chunks[seq_num].data, payload + 8, text_payload_len);
                    chunks[seq_num].length = text_payload_len;
                    chunks[seq_num].received = 1;
                    
                    if (total_chunks_expected == 0 || (int)total_chunks > total_chunks_expected) {
                        total_chunks_expected = total_chunks;
                    }
                    
                    if ((int)seq_num > max_chunk_received) {
                        max_chunk_received = seq_num;
                    }
                    
                    // Check if we have all chunks
                    if (all_chunks_received()) {
                        process_complete_message(packet_arrival_cycles);
                    }
                }
            } else {
                // Handle as plain text for backward compatibility
                char *text_payload = malloc(udp_payload_len + 1);
                memcpy(text_payload, payload, udp_payload_len);
                text_payload[udp_payload_len] = '\0';
                
                fprintf(stderr, "Received plain text: %s\n", text_payload);
                
                // Tokenize using WordPiece
                char tokens[MAX_TOKENS][MAX_TOKEN_LEN];
                int num_tokens = dpdk_wordpiece_tokenize(text_payload, tokens, MAX_TOKENS);
                
                uint64_t tokenize_cycles = rte_rdtsc();
                
                // Output results
                printf("DPDK_TOKENIZATION_START\n");
                printf("PACKET_ARRIVAL_TIME: %lu\n", packet_arrival_cycles);
                printf("TOKENIZE_END_TIME: %lu\n", tokenize_cycles);
                printf("TSC_FREQUENCY: %lu\n", tsc_hz);
                printf("ORIGINAL_TEXT: %s\n", text_payload);
                printf("NUM_TOKENS: %d\n", num_tokens);
                printf("TOKENS: ");
                for (int i = 0; i < num_tokens; i++) {
                    printf("%s", tokens[i]);
                    if (i < num_tokens - 1) printf(" ");
                }
                printf("\n");
                printf("TOKEN_IDS: ");
                for (int i = 0; i < num_tokens; i++) {
                    int token_id = dpdk_wordpiece_get_id_by_token(tokens[i]);
                    printf("%d", token_id);
                    if (i < num_tokens - 1) printf(" ");
                }
                printf("\n");
                printf("DPDK_TOKENIZATION_END\n");
                fflush(stdout);
                
                double total_latency_us = (double)(tokenize_cycles - packet_arrival_cycles) * 1000000.0 / tsc_hz;
                fprintf(stderr, "DPDK_LATENCY: %.2f us\n", total_latency_us);
                
                free(text_payload);
            }
            
            rte_pktmbuf_free(m);
        }
    }

    // Cleanup
    dpdk_wordpiece_cleanup();
    return EXIT_SUCCESS;
}
