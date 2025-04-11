import socket
import os

HOST = '0.0.0.0'
PORT = 9001
SAVE_DIR = 'uploads'

os.makedirs(SAVE_DIR, exist_ok=True)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"🎬 Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"📡 Connection from {addr}")
            file_size_bytes = conn.recv(32)
            file_size = int.from_bytes(file_size_bytes, 'big')

            filename = f"video_{addr[1]}.mp4"
            filepath = os.path.join(SAVE_DIR, filename)

            with open(filepath, 'wb') as f:
                remaining = file_size
                while remaining > 0:
                    chunk = conn.recv(min(1400, remaining))
                    if not chunk:
                        break
                    f.write(chunk)
                    remaining -= len(chunk)

            print(f"✅ Received {filename} ({file_size} bytes)")
            conn.sendall(b"UPLOAD_SUCCESS".ljust(16))
