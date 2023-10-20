import socket
import time
import cv2 as cv
import numpy as np
import threading

HOST = '192.168.0.2'
PORT = 19122
BUFFER_SIZE = 1048576

def start_receiver():
    global reconstructed_frame
    while True:
        user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        user_socket.connect((HOST,PORT))
        received_data = b''
        while True:
            data_chunk = user_socket.recv(BUFFER_SIZE)
            if not data_chunk:
                break
            received_data += data_chunk
        
        frame_data = np.frombuffer(received_data, dtype=np.uint8)
        reconstructed_frame = cv.imdecode(frame_data, cv.IMREAD_COLOR)
        print(reconstructed_frame)
        # time.sleep(0)

receiver_thread = threading.Thread(target=start_receiver)
receiver_thread.start()
time.sleep(3)

while True:
    cv.imshow('Received Frame', reconstructed_frame)
    if cv.waitKey(1) == ord('q'):
        break