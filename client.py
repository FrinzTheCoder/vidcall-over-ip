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
        user_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        user_socket.sendto("Hello My Friend!".encode('utf-8'), (HOST, PORT))

        message_address = user_socket.recvfrom(BUFFER_SIZE)
        message = message_address[0]
        address = message_address[1]

        frame_data = np.frombuffer(message, dtype=np.uint8)
        reconstructed_frame = cv.imdecode(frame_data, cv.IMREAD_COLOR)
        print(reconstructed_frame)

receiver_thread = threading.Thread(target=start_receiver)
receiver_thread.start()
time.sleep(2)

while True:
    cv.imshow('Received Frame', reconstructed_frame)
    if cv.waitKey(1) == ord('q'):
        break