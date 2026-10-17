#!/usr/bin/env python3

import socket
import sys

def send_simple_udp(message, target_ip="localhost", target_port=6000):
    """Send a simple UDP packet (no chunking) for basic connectivity testing"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending simple message to {target_ip}:{target_port}: {message}")
    sock.sendto(message.encode('utf-8'), (target_ip, target_port))
    sock.close()
    print("Simple message sent!")

if __name__ == "__main__":
    message = "test1 test1 test1 test1 test1 test1"
    target_ip = "localhost"
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    
    print("Simple UDP Test - sends a single packet without chunking")
    print("Usage: python3 test_simple_udp.py [message]")
    print("Note: For DPDK version, you may need to specify the interface IP")
    print()
    
    send_simple_udp(message, target_ip, 6000)
