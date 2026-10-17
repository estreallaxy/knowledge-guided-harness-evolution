#!/usr/bin/env python3

import socket
import math

def chunked_send_udp(text: str, guest_ip: str, guest_port: int):
    """
    Splits text into MTU-safe chunks, each prefixed by an 8-byte header:
    - 4 bytes: sequence number (big-endian)
    - 4 bytes: total chunk count (big-endian)
    """
    MTU_PAYLOAD = 1200 - 4  # Subtract 4 bytes for the new total_chunks field
    data = text.encode('utf-8')
    total = len(data)
    sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    num_chunks = math.ceil(total / MTU_PAYLOAD)

    for idx in range(num_chunks):
        start = idx * MTU_PAYLOAD
        end   = start + MTU_PAYLOAD
        chunk = data[start:end]
        # 8-byte header: 4-byte sequence + 4-byte total chunks
        header = idx.to_bytes(4, byteorder='big') + num_chunks.to_bytes(4, byteorder='big')
        sock.sendto(header + chunk, (guest_ip, guest_port))
        print(f"Sent chunk {idx+1}/{num_chunks} ({len(chunk)} bytes)")

    sock.close()

if __name__ == "__main__":
    # Test with standard message
    guest_ip   = "localhost"
    guest_port = 6000
    user_query = "test test1 test1 test1 test1 test1 test1 test1 test1"
    
    print(f"Chunked UDP Test - sends message in multiple packets with 8-byte headers")
    print(f"Sending chunked message to {guest_ip}:{guest_port}")
    print(f"Message: {user_query}")
    print()
    chunked_send_udp(user_query, guest_ip, guest_port)
    print("Message sent!")
