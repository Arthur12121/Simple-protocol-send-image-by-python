import socket
import base64
import cv2
import numpy as np

def proto(sock, number):
    data = b''
    while len(data) < number:
        chunk = sock.recv(number - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def get_img(client):
    full_part_img = b''
    while True:
        header = proto(client, 4)
        if not header:
            break  

        len_header = proto(client, 1)
        if not len_header:
            break

        num_len_part_img = proto(client, 1)
        if not num_len_part_img:
            break
        num_len_part_img = int(num_len_part_img.decode())

        len_part_img = proto(client, num_len_part_img)
        if not len_part_img:
            break
        len_part_img = int(len_part_img.decode())

        part_img = proto(client, len_part_img)
        if not part_img:
            break

        full_part_img += part_img

    print("All parts received and combined")
    return full_part_img

SERVER_IP = "192.168.1.204" # you can chenge the ip 
SERVER_PORT = 8080

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

while True:
    try:
        full_img = get_img(client)
        print("img complete")
        if not full_img:
            print("No data received")
            continue

        try:
            img_bytes = base64.b64decode(full_img)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            print("Decoding error:", e)
            img = None

        if img is None:
            print("Image decoding failed!")
        else:
            cv2.imshow("Image", img)
            if cv2.waitKey(0) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

    except Exception as e:
        print("Connection error:", e)
        break
