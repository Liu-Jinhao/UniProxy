import socket
import threading
import time

HOST = '0.0.0.0'
PORT = 5000
BUFFER_SIZE = 4096

def handle_client(conn, addr):
    print(f"[+] Client {addr} connected")
    try:
        request = ""
        while True:
            request += conn.recv(1024).decode()
            if request[-1] == "\n":
                break
        params = request.strip().split()

        if len(params) < 2:
            print("ERROR: Invalid request format\n")
            return

        mode = params[0]  # "size" or "rate"
        if mode == "size":
            try:
                size = int(params[1])  # Requested data size
                send_fixed_size_data(conn, size)
            except ValueError:
                print("ERROR: Invalid size format\n")

        elif mode == "rate":
            try:
                rate = float(params[1])  # Data rate (bytes per second)
                send_fixed_rate(conn, rate)
            except ValueError:
                print("ERROR: Invalid rate format\n")

        else:
            print(b"ERROR: Unknown mode\n")

    except Exception as e:
        print(f"[!] Error handling client {addr}: {e}")

    finally:
        conn.close()
        print(f"[-] Client {addr} disconnected")


def send_fixed_size_data(conn, size):
    data = b'X' * size  # Generate the full data block
    conn.sendall(data)
    print(f"[✓] Sent {size} bytes in one transmission")


def send_fixed_rate(conn, rate):
    print(f"[→] Sending data at {rate} Mbps")
    chunk_size = BUFFER_SIZE
    chunk = b'X' * chunk_size  # Fixed-size chunk

    start_time = time.time()
    sent_bytes = 0

    try:
        while True:
            conn.sendall(chunk)
            sent_bytes += chunk_size

            elapsed = time.time() - start_time
            expected_time = sent_bytes / (rate/8)
            sleep_time = expected_time - elapsed

            if sleep_time > 0:
                time.sleep(sleep_time)  # Maintain the specified rate
    except (BrokenPipeError, ConnectionResetError):
        print(f"[!] Client disconnected")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"[*] Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
