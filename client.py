import socket
import time
import cv2 as cv
import numpy as np
import threading
import pickle

HOST = '192.168.0.2'
PORT = 19122
BUFFER_SIZE = 10485760
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
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
    while True:        
        global CONNECTIONS
        user_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        user_socket.bind(('192.168.0.2', 19123))
        user_socket.sendto(frame_bytes, (HOST, PORT))
        print("sent data")

        message_address = user_socket.recvfrom(BUFFER_SIZE)
        received_data = message_address[0]
        print("received data")

        user_socket.close()
        CONNECTIONS = pickle.loads(received_data)
        # time.sleep(0.2)

receiver_thread = threading.Thread(target=start_receiver)
receiver_thread.start()

while True:
    for host in CONNECTIONS.keys():
        frame_data = np.frombuffer(CONNECTIONS[host], dtype=np.uint8)
        try:
            reconstructed_frame = cv.imdecode(frame_data, cv.IMREAD_COLOR)
            cv.imshow(str(host),reconstructed_frame)
            if cv.waitKey(1) == ord('q'):
                break
        except:
            time.sleep(1)