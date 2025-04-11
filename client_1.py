import socket
import os

HOST = input("Enter server IP (e.g. 127.0.0.1): ").strip()
PORT = 9001
file_path = input("Enter path to .mp4 file: ").strip()

if not file_path.endswith(".mp4") or not os.path.isfile(file_path):
    print("❌ Please provide a valid .mp4 file.")
    exit()

file_size = os.path.getsize(file_path)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(file_size.to_bytes(32, 'big'))

    with open(file_path, 'rb') as f:
        while (chunk := f.read(1400)):
            s.sendall(chunk)

    response = s.recv(16).decode().strip()
    print(f"📩 Server response: {response}")
