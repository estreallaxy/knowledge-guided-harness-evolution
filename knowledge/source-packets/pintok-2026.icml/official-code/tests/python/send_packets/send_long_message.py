#!/usr/bin/env python3

import send_chunked
import sys

def test_long_message(target_ip="localhost", target_port=6000, repeat_count=50):
    """Test with a long message that will require multiple chunks"""
    # Create a long message that will require multiple chunks
    base_text = 'test1 test1 test1 test1 test1 test1 test1 test1 test1 test1 '
    long_text = base_text * repeat_count
    
    print(f'Long Message Test - Multiple Chunks Required')
    print(f'Sending {len(long_text)} characters ({repeat_count} repetitions)')
    print(f'Target: {target_ip}:{target_port}')
    print()
    
    send_chunked.chunked_send_udp(long_text, target_ip, target_port)
    print("Long message sent!")

if __name__ == "__main__":
    target_ip = "localhost"
    repeat_count = 50
    
    # Allow command line arguments for IP
    if len(sys.argv) > 1:
        target_ip = sys.argv[1]
    if len(sys.argv) > 2:
        repeat_count = int(sys.argv[2])
    
    print("Usage: python3 test_long_message.py [target_ip] [repeat_count]")
    print("Note: For DPDK version, use the interface IP (e.g., 192.168.122.28)")
    print()
    
    test_long_message(target_ip, 6000, repeat_count)
