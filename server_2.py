import socket
import json
import os
import subprocess

HOST = '0.0.0.0'
PORT = 9002
BUFFER_SIZE = 1400
TEMP_DIR = 'uploads'

os.makedirs(TEMP_DIR, exist_ok=True)

def receive_exact(sock, num_bytes):
    data = b''
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            break
        data += packet
    return data

def handle_client(conn):
    header = receive_exact(conn, 8)
    json_len = int.from_bytes(header[:2], 'big')
    media_len = int.from_bytes(header[2:3], 'big')
    payload_len = int.from_bytes(header[3:], 'big')

    json_data = receive_exact(conn, json_len).decode()
    media_type = receive_exact(conn, media_len).decode()
    payload = receive_exact(conn, payload_len)

    data = json.loads(json_data)
    op = data['operation']
    filename = os.path.join(TEMP_DIR, f"{data['filename']}")

    with open(filename, 'wb') as f:
        f.write(payload)

    output_path = filename

    if op == 'compress':
        output_path = filename.replace('.mp4', '_compressed.mp4')
        subprocess.run(['ffmpeg', '-i', filename, '-vcodec', 'libx264', '-crf', '28', output_path])

    with open(output_path, 'rb') as f:
        result = f.read()

    # Send response using same protocol
    result_json = json.dumps({"status": "OK"}).encode()
    result_header = len(result_json).to_bytes(2, 'big') + len(media_type.encode()).to_bytes(1, 'big') + len(result).to_bytes(5, 'big')

    conn.sendall(result_header)
    conn.sendall(result_json)
    conn.sendall(media_type.encode())
    conn.sendall(result)

    conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"🚀 Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        print(f"📥 Connection from {addr}")
        handle_client(conn)
