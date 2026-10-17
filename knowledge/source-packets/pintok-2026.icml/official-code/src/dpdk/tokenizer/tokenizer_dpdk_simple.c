// tokenizer_dpdk_simple.c - DPDK-based simple tokenizer

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>       // for ntohs()
#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_mbuf.h>
#include <rte_ether.h>
#include <rte_ip.h>
#include <rte_udp.h>
#include <rte_mempool.h>
#include <rte_cycles.h>      // for TSC timing
#include "util.h"            // your JSON dictionary loader + lookup

#define PORT_ID        0
#define RX_QUEUE_ID    0
#define TX_QUEUE_ID    0
#define BURST_SIZE     32
#define LISTEN_PORT    6000
#define NUM_MBUFS      8191
#define MBUF_CACHE_SIZE 250
#define MAX_CHUNKS     1000
#define MAX_TEXT_SIZE  (MAX_CHUNKS * 1200)

// Structure to store received chunks (similar to woDPDK version)
struct chunk_data {
    char data[1200];
    int length;
    int received;
};

static struct chunk_data chunks[MAX_CHUNKS];
static int max_chunk_received = -1;
static int total_chunks_expected = 0;  // New: track expected total chunks

// Latency statistics
static uint64_t min_latency_cycles = UINT64_MAX;
static uint64_t max_latency_cycles = 0;
static uint64_t total_latency_cycles = 0;
static uint64_t processed_packet_count = 0;
static uint64_t tsc_hz = 0;  // TSC frequency for conversion to microseconds

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

// Function to process complete message
void process_complete_message(void) {
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
    
    fprintf(stderr, "Processing complete message: %s\n", complete_text);
    
    // Tokenize & lookup
    char *saveptr = NULL;
    char *word = strtok_r(complete_text, " \t\n", &saveptr);
    while (word) {
        int id = lookup_token(word);
        printf("%d ", id);
        word = strtok_r(NULL, " \t\n", &saveptr);
    }
    printf("\n");
    fflush(stdout);
    
    uint64_t end_cycles = rte_rdtsc();
    
    // Calculate latencies
    uint64_t total_latency = end_cycles - start_cycles;
    uint64_t tokenize_latency = end_cycles - assembly_cycles;
    double total_us = (double)total_latency * 1000000.0 / tsc_hz;
    double tokenize_us = (double)tokenize_latency * 1000000.0 / tsc_hz;
    
    fprintf(stderr, "LATENCY_BREAKDOWN: assembly=%.2f tokenize=%.2f total=%.2f us\n",
           (double)(assembly_cycles - start_cycles) * 1000000.0 / tsc_hz,
           tokenize_us, total_us);
    
    // Update statistics
    min_latency_cycles = (total_latency < min_latency_cycles) ? total_latency : min_latency_cycles;
    max_latency_cycles = (total_latency > max_latency_cycles) ? total_latency : max_latency_cycles;
    total_latency_cycles += total_latency;
    processed_packet_count++;
    
    // Reset for next message
    memset(chunks, 0, sizeof(chunks));
    max_chunk_received = -1;
    total_chunks_expected = 0;
    
    free(complete_text);
}

// Function to check if all chunks are received based on total expected
int all_chunks_received(void) {
    if (total_chunks_expected <= 0) {
        return 0;  // Don't know total yet
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
        fprintf(stderr, "Usage: %s <dictionary.json> [DPDK EAL args...]\n", argv[0]);
        return EXIT_FAILURE;
    }
    const char *dict_file = argv[1];

    // 1) load your JSON word - ID mapping
    if (read_json_dictionary(dict_file) != 0) {
        fprintf(stderr, "Error: could not load dictionary '%s'\n", dict_file);
        return EXIT_FAILURE;
    }

    // 2) initialize DPDK EAL
    int ret = rte_eal_init(argc, argv);
    if (ret < 0)
        rte_exit(EXIT_FAILURE, "Failed to initialize DPDK EAL\n");

    // Initialize TSC frequency for latency measurements
    tsc_hz = rte_get_tsc_hz();
    fprintf(stderr, "TSC frequency: %lu Hz\n", tsc_hz);

    // 3) Check if we have any ports
    uint16_t nb_ports = rte_eth_dev_count_avail();
    if (nb_ports == 0)
        rte_exit(EXIT_FAILURE, "No Ethernet ports - bye\n");

    // 4) Create mbuf pool
    struct rte_mempool *mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", NUM_MBUFS,
        MBUF_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE, rte_socket_id());
    if (mbuf_pool == NULL)
        rte_exit(EXIT_FAILURE, "Cannot create mbuf pool\n");

    // 5) Configure the Ethernet device
    struct rte_eth_conf port_conf = {0};
    port_conf.rxmode.mq_mode = RTE_ETH_MQ_RX_NONE;
    
    if (rte_eth_dev_configure(PORT_ID, 1, 1, &port_conf) < 0)
        rte_exit(EXIT_FAILURE, "Cannot configure port %u\n", PORT_ID);

    // 6) Set up RX queue
    if (rte_eth_rx_queue_setup(PORT_ID, RX_QUEUE_ID, 128,
                               rte_eth_dev_socket_id(PORT_ID),
                               NULL, mbuf_pool) < 0)
        rte_exit(EXIT_FAILURE, "RX queue setup failed\n");

    // 7) Set up TX queue  
    if (rte_eth_tx_queue_setup(PORT_ID, TX_QUEUE_ID, 512,
                               rte_eth_dev_socket_id(PORT_ID),
                               NULL) < 0)
        rte_exit(EXIT_FAILURE, "TX queue setup failed\n");

    // 8) Start the Ethernet port
    if (rte_eth_dev_start(PORT_ID) < 0)
        rte_exit(EXIT_FAILURE, "Cannot start port %u\n", PORT_ID);

    // 9) Enable promiscuous mode (to receive all packets)
    if (rte_eth_promiscuous_enable(PORT_ID) != 0)
        rte_exit(EXIT_FAILURE, "Cannot enable promiscuous mode\n");

    struct rte_eth_link link;
    int ret_link = rte_eth_link_get_nowait(PORT_ID, &link);
    if (ret_link != 0) {
        fprintf(stderr, "Warning: Could not get link status\n");
    }
    
    fprintf(stderr, "DPDK tokenizer initialized successfully\n");
    fprintf(stderr, "Port %u: Link %s, Speed %u Mbps\n", PORT_ID,
           link.link_status ? "UP" : "DOWN", link.link_speed);
    fprintf(stderr, "Listening for UDP packets on port %u\n", LISTEN_PORT);

    // 10) Main packet processing loop
    struct rte_mbuf *bufs[BURST_SIZE];
    unsigned long total_packets = 0;
    unsigned long processed_packets = 0;
    
    while (1) {
        uint16_t nb_rx = rte_eth_rx_burst(PORT_ID, RX_QUEUE_ID, bufs, BURST_SIZE);
        if (nb_rx == 0)
            continue;
            
        total_packets += nb_rx;
        
        for (uint16_t i = 0; i < nb_rx; ++i) {
            struct rte_mbuf *m = bufs[i];
            
            // Start timing as soon as we get the packet
            uint64_t packet_start_cycles = rte_rdtsc();
            
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
            
            processed_packets++;
            
            // Process payload (handle both new 8-byte and old 4-byte headers)
            if (udp_payload_len >= 8) {
                // New format: 8-byte header (seq_num + total_chunks)
                uint32_t seq_num, total_chunks;
                extract_chunk_header(payload, &seq_num, &total_chunks);
                
                // Extract text payload (after 8-byte header)
                int text_payload_len = udp_payload_len - 8;
                
                fprintf(stderr, "Received chunk %u/%u, payload length: %d\n", 
                       seq_num, total_chunks, text_payload_len);
                
                // Store chunk data
                if (seq_num < MAX_CHUNKS && text_payload_len > 0) {
                    memcpy(chunks[seq_num].data, payload + 8, text_payload_len);
                    chunks[seq_num].length = text_payload_len;
                    chunks[seq_num].received = 1;
                    
                    // Update expected total chunks
                    if (total_chunks_expected == 0 || (int)total_chunks > total_chunks_expected) {
                        total_chunks_expected = total_chunks;
                    }
                    
                    if ((int)seq_num > max_chunk_received) {
                        max_chunk_received = seq_num;
                    }
                    
                    // Check if we have all chunks
                    if (all_chunks_received()) {
                        process_complete_message();
                    }
                }
            } else if (udp_payload_len >= 4) {
                // Old format: 4-byte header (seq_num only) - for backward compatibility
                uint32_t seq_num = ((uint32_t)(unsigned char)payload[0] << 24) |
                                  ((uint32_t)(unsigned char)payload[1] << 16) |
                                  ((uint32_t)(unsigned char)payload[2] << 8) |
                                  ((uint32_t)(unsigned char)payload[3]);
                
                // Extract text payload (after 4-byte header)
                int text_payload_len = udp_payload_len - 4;
                
                fprintf(stderr, "Received chunk %u (old format), payload length: %d\n", seq_num, text_payload_len);
                
                // Store chunk data
                if (seq_num < MAX_CHUNKS && text_payload_len > 0) {
                    memcpy(chunks[seq_num].data, payload + 4, text_payload_len);
                    chunks[seq_num].length = text_payload_len;
                    chunks[seq_num].received = 1;
                    
                    if ((int)seq_num > max_chunk_received) {
                        max_chunk_received = seq_num;
                    }
                    
                    // For old format, we use the old heuristic (all chunks up to max)
                    int old_style_complete = 1;
                    for (int i = 0; i <= max_chunk_received; i++) {
                        if (!chunks[i].received) {
                            old_style_complete = 0;
                            break;
                        }
                    }
                    if (old_style_complete && max_chunk_received >= 0) {
                        process_complete_message();
                    }
                }
            } else {
                // Handle as plain text (for backward compatibility)
                char *text_payload = malloc(udp_payload_len + 1);
                memcpy(text_payload, payload, udp_payload_len);
                text_payload[udp_payload_len] = '\0';
                
                fprintf(stderr, "Received plain text: %s\n", text_payload);
                
                char *saveptr = NULL;
                char *word = strtok_r(text_payload, " \t\n", &saveptr);
                while (word) {
                    int id = lookup_token(word);
                    printf("%d ", id);
                    word = strtok_r(NULL, " \t\n", &saveptr);
                }
                printf("\n");
                fflush(stdout);
                
                // Calculate and report packet latency
                uint64_t packet_end_cycles = rte_rdtsc();
                uint64_t packet_latency = packet_end_cycles - packet_start_cycles;
                double packet_latency_us = (double)packet_latency * 1000000.0 / tsc_hz;
                
                fprintf(stderr, "PACKET_LATENCY: %.2f us (%lu cycles)\n", 
                       packet_latency_us, packet_latency);
                
                // Update statistics
                min_latency_cycles = (packet_latency < min_latency_cycles) ? packet_latency : min_latency_cycles;
                max_latency_cycles = (packet_latency > max_latency_cycles) ? packet_latency : max_latency_cycles;
                total_latency_cycles += packet_latency;
                processed_packet_count++;
                
                free(text_payload);
            }
            
            rte_pktmbuf_free(m);
        }
        
        // Print stats occasionally
        if (total_packets % 1000 == 0 && total_packets > 0) {
            fprintf(stderr, "PACKET_STATS: Total: %lu, Processed: %lu\n", 
                   total_packets, processed_packets);
                   
            if (processed_packet_count > 0) {
                double min_us = (double)min_latency_cycles * 1000000.0 / tsc_hz;
                double max_us = (double)max_latency_cycles * 1000000.0 / tsc_hz;
                double avg_us = (double)total_latency_cycles * 1000000.0 / tsc_hz / processed_packet_count;
                
                fprintf(stderr, "LATENCY_STATS: min=%.2f max=%.2f avg=%.2f us (over %lu packets)\n",
                       min_us, max_us, avg_us, processed_packet_count);
            }
        }
    }

    return EXIT_SUCCESS;
}
