import socket
import math

MTU_PAYLOAD = 1200  # bytes, leave headroom for IP/UDP headers

def chunked_send_udp(text: str, guest_ip: str, guest_port: int):
    """
    Splits text into MTU-safe chunks, each prefixed by a 4-byte
    sequence number so the guest can reassemble in order.
    """
    data = text.encode('utf-8')
    total = len(data)
    sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    num_chunks = math.ceil(total / MTU_PAYLOAD)

    for idx in range(num_chunks):
        start = idx * MTU_PAYLOAD
        end   = start + MTU_PAYLOAD
        chunk = data[start:end]
        # 4-byte big-endian sequence header
        header = idx.to_bytes(4, byteorder='big')
        sock.sendto(header + chunk, (guest_ip, guest_port))
        print(f"Sent chunk {idx+1}/{num_chunks} ({len(chunk)} bytes)")

    sock.close()

if __name__ == "__main__":
    guest_ip   = "192.168.122.28"
    guest_port = 6000
    user_query = "test1 test1 test1 test1 test1 test1 test1 test1 test1 test1" * 10
    chunked_send_udp(user_query, guest_ip, guest_port)