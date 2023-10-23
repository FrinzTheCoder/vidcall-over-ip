import socket
import time
import cv2 as cv
import numpy as np
import threading
import json
import base64

HOST = '192.168.1.4'
PORT = 19122
BUFFER_SIZE = 1048576
FRAME_WIDTH = 400
FRAME_HEIGHT = 300
CONNECTIONS = dict()

frame_bytes = b''
def start_camera():
    cap = cv.VideoCapture(0)
    cap.set(3, FRAME_WIDTH)
    cap.set(4, FRAME_HEIGHT)

    while True:
        global frame_bytes
        global frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        frame = cv.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        frame_bytes = cv.imencode('.jpg',frame)[1].tobytes()

    cap.release()
    cv.destroyAllWindows()

camera_thread = threading.Thread(target=start_camera)
camera_thread.start()

while frame_bytes == b'':
    pass

def start_receiver():  
    global CONNECTIONS
    user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    user_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    # user_socket.bind(('192.168.0.10', 19122))
    user_socket.connect((HOST,PORT))
    
    while True:
        packet = {
            "type":"image",
            "content":base64.b64encode(frame_bytes).decode('utf-8')}
        json_string = json.dumps(packet)
        encoded_data = json_string.encode('utf-8')

        user_socket.sendall(encoded_data + b'END')

        received_data = b''
        while True:
            data_chunk = user_socket.recv(BUFFER_SIZE)
            received_data += data_chunk
            if b'END' in received_data:
                received_data = received_data[:len(received_data)-3]
                break
        try:
            json_string = received_data.decode('utf-8')
            CONNECTIONS = json.loads(json_string)
        except:
            CONNECTIONS = dict()
            print("ERROR PICKLE TRUNCATED2")
        time.sleep(0.2)
        
receiver_thread = threading.Thread(target=start_receiver)
receiver_thread.start()

while True:
    try:
        for host in CONNECTIONS.keys():
            frame_data = np.frombuffer(base64.b64decode(CONNECTIONS[host].encode('utf-8')), 
                                       dtype=np.uint8)
            try:
                reconstructed_frame = cv.imdecode(frame_data, cv.IMREAD_COLOR)
                cv.imshow(str(host),reconstructed_frame)
                if cv.waitKey(1) == ord('q'):
                    break
            except:
                time.sleep(1)
    except:
        print("ERROR")