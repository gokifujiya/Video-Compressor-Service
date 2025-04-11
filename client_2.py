import socket
import json
import os

server_ip = input("Enter server IP: ")
filename = input("Enter path to .mp4 file: ")

operation = input("Operation (compress/convert/etc.): ")
media_type = 'mp4'

with open(filename, 'rb') as f:
    payload = f.read()

json_payload = json.dumps({
    "operation": operation,
    "filename": os.path.basename(filename)
}).encode()

header = len(json_payload).to_bytes(2, 'big') + len(media_type.encode()).to_bytes(1, 'big') + len(payload).to_bytes(5, 'big')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_ip, 9002))
sock.sendall(header)
sock.sendall(json_payload)
sock.sendall(media_type.encode())
sock.sendall(payload)

# Receive response
header = sock.recv(8)
json_len = int.from_bytes(header[:2], 'big')
media_len = int.from_bytes(header[2:3], 'big')
payload_len = int.from_bytes(header[3:], 'big')

response_json = sock.recv(json_len).decode()
media = sock.recv(media_len).decode()
result = sock.recv(payload_len)

output_path = 'output_from_server.' + media
with open(output_path, 'wb') as f:
    f.write(result)

print(f"✅ Saved processed file as {output_path}")
sock.close()
