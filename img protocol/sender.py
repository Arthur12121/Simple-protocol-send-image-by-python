import socket
import time
import base64
import cv2
import subprocess

def ip_get():
    cmd_ip = subprocess.check_output("ipconfig", shell=True).decode(errors="ignore")
    for lines in cmd_ip.splitlines():
        lines = lines.strip()
        if "IPv4" in lines and ":" in lines:
            ip = lines.split(":")[-1].strip()
            return ip
    return "127.0.0.1"

def split_message_max4048(data):
    if isinstance(data, str):
        data = data.encode()
    MAX_SIZE = 4048
    parts = []
    for i in range(0, len(data), MAX_SIZE):
        part = data[i:i + MAX_SIZE]
        parts.append(part)
    return parts


SERVER_IP = ip_get()
SERVER_PORT = 8080

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, SERVER_PORT))
server.listen()
print("Waiting for client...")
conn, addr = server.accept()
print("Client connected:", addr)


cam = cv2.VideoCapture(0)
ret, frame = cam.read()
cam.release()

if not ret:
    print("Failed to capture image")
    conn.close()
    server.close()
    exit()


ret_img, img_encoded = cv2.imencode('.jpg', frame)
img_bytes = img_encoded.tobytes()
img_base64 = base64.b64encode(img_bytes)


parts = split_message_max4048(img_base64)


for part_img in parts:
    len_part_img = str(len(part_img))             
    num_len_part_img = str(len(len_part_img))      

    header = b'0x334'                             
    num_len_b = num_len_part_img.encode()          
    len_b = len_part_img.encode()                  

    msg = header + num_len_b + len_b + part_img
    conn.sendall(msg)                               
    time.sleep(0.05)

print("All parts sent successfully")
conn.close()
server.close()
