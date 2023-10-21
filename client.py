import socket
import time
import cv2 as cv
import numpy as np
import threading
import pickle

HOST = '192.168.0.2'
PORT = 19122
BUFFER_SIZE = 1048576
FRAME_WIDTH = 200
FRAME_HEIGHT = 112
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

# def send_thread(user_socket, frame_bytes):
#     user_socket.send(frame_bytes)

def start_receiver():
    while True:
        try:
            global CONNECTIONS
            user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            user_socket.bind(('192.168.0.10',19122))
            user_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            user_socket.connect((HOST,PORT))

            # sending_thread = threading.Thread(target=send_thread,
            #                                   args=(user_socket, frame_bytes))
            # sending_thread.start()
            user_socket.send(frame_bytes)
            print("sending data")

            received_data = b''
            while True:
                data_chunk = user_socket.recv(BUFFER_SIZE)
                if not data_chunk:
                    break
                received_data += data_chunk
            print("received data")
            user_socket.close()
            CONNECTIONS = pickle.loads(received_data)
            time.sleep(0.3)
        except:
            print("TIMEOUT!")
            time.sleep(2)
            print("STARTING AGAIN")

receiver_thread = threading.Thread(target=start_receiver)
receiver_thread.start()

while True:
    for host in CONNECTIONS.keys():
        frame_data = np.frombuffer(CONNECTIONS[host], dtype=np.uint8)
        reconstructed_frame = cv.imdecode(frame_data, cv.IMREAD_COLOR)
        cv.imshow(str(host),reconstructed_frame)
        if cv.waitKey(1) == ord('q'):
            break