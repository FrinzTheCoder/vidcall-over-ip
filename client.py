import socket
import time
import cv2 as cv
import numpy as np
import threading
import pickle

HOST = '192.168.0.2'
PORT = 19122
BUFFER_SIZE = 20480
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CONNECTIONS = dict()
BUFFER = b''

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
        global BUFFER
        user_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        user_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        user_socket.bind(('192.168.0.2', 19123))
        
        chunks = [frame_bytes[i:i+BUFFER_SIZE] for i in range(0, len(frame_bytes), BUFFER_SIZE)]
        for chunk in chunks:
            print(len(chunk))
            user_socket.sendto(chunk, (HOST, PORT))
        user_socket.sendto(b'END', (HOST, PORT))
        print("sent data")

        while True:
            message_address = user_socket.recvfrom(BUFFER_SIZE)
            received_data = message_address[0]
            print(received_data[-1])
        
            if received_data == b'END' or received_data == b'':
                CONNECTIONS = pickle.loads(BUFFER)
                BUFFER = b''
                print("END OF FILE")
                break
            else:
                BUFFER += received_data
        user_socket.close()
        # time.sleep()
        
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