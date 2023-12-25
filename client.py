import socket
import time
import cv2 as cv
import numpy as np
import threading
import json
import base64
import tkinter as tk
from codex import encode, decode
from ui import UserInterface

# DONT FORGET TO SET HOST AND PORT TO THE RIGHT VALUE
HOST = '192.168.0.2'
PORT = 19122
PORT_SENDER = 19123
PORT_RECEIVER = 19124
BUFFER_SIZE = 1048576
FRAME_WIDTH = 1600
FRAME_HEIGHT = 900
CONNECTIONS = dict()
COMPRESSION_PARAMS = [cv.IMWRITE_JPEG_QUALITY, 100]
PIN = 19122

GENERAL_INFORMATION = {
    'HOST':HOST,
    'PORT':PORT,
    'PORT_SENDER':PORT_SENDER,
    'PORT_RECEIVER':PORT_RECEIVER,
    'BUFFER_SIZE':BUFFER_SIZE,
    'FRAME_WIDTH':FRAME_WIDTH,
    'FRAME_HEIGHT':FRAME_HEIGHT,
    'COMPRESSION_PARAMS':COMPRESSION_PARAMS
}

# main socket
user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# user_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
user_socket.connect((HOST,PORT))
print("CONNECTING USER SOCKET SUCESS")

# sender socket
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sender_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sender_socket.connect((HOST, PORT_SENDER))
print("CONNECTING SENDER SOCKET SUCESS")

# receiver socket
receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# receiver_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
receiver_socket.connect((HOST, PORT_RECEIVER))
print("CONNECTING RECEIVER SOCKET SUCESS")

# request connection with PIN
type = 'CONNECTION_REQUEST'
content = '19122'
payload = encode(type, content)
user_socket.send(payload)

# response - check whether the pin is valid or not
payload = user_socket.recv(BUFFER_SIZE)
type, content = decode(payload)
if content == 'REJECTED':
    print("CONNECTION FAILED: INCORRECT PIN")
    user_socket.close()
    sender_socket.close()
    receiver_socket.close()
    exit()
print("CONNECTION SUCCESS: PIN CORRECT")

# request for source info
type = 'CONNECTION_SOURCE_REQUEST'
content = 'Python'
payload = encode(type, content)
user_socket.send(payload)

# response - check whether the source type is valid
payload = user_socket.recv(BUFFER_SIZE)
type, content = decode(payload)
if content == 'INVALID':
    print("CONNECTION FAILED: INVALID SOURCE TYPE")
    user_socket.close()
    sender_socket.close()
    receiver_socket.close()
    exit()
else:
    print("CONNECTION SUCCESS: SOURCE TYPE PYTHON")
print(f"SUCCESSFULLY CONNECTED TO SERVER  {HOST}")

# declaring user interface
root = tk.Tk()
user_interface = UserInterface(root, user_socket, sender_socket, receiver_socket, GENERAL_INFORMATION)
root.mainloop()

# closing the application
user_socket.close()
sender_socket.close()
receiver_socket.close()
print("APPLICATION CLOSED")

# setting up the camera
# frame_bytes = b''
# def start_camera():
#     cap = cv.VideoCapture(0)
#     cap.set(3, FRAME_WIDTH)
#     cap.set(4, FRAME_HEIGHT)

#     # camera capture main loop
#     while True:
#         global frame_bytes
#         global frame
#         ret, frame = cap.read()
#         if not ret:
#             print("Error: Failed to capture frame.")
#             break
#         frame = cv.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
#         frame_bytes = cv.imencode('.jpg', frame, COMPRESSION_PARAMS)[1].tobytes()

#     cap.release()
#     cv.destroyAllWindows()

# start camera thread
# camera_thread = threading.Thread(target=start_camera)
# camera_thread.start()

# wait until at least there exist one captured frame
# while frame_bytes == b'':
#     pass
    
    # # receiver main loop
    # while True:

    #     # sending data to server
    #     packet = {
    #         "type":"image",
    #         "content":base64.b64encode(frame_bytes).decode('utf-8')}
    #     json_string = json.dumps(packet)
    #     encoded_data = json_string.encode('utf-8')

    #     user_socket.sendall(encoded_data + b'END')

    #     # receiving data from server
    #     received_data = b''
    #     while True:
    #         data_chunk = user_socket.recv(BUFFER_SIZE)
    #         received_data += data_chunk
    #         if b'END' in received_data:
    #             received_data = received_data[:len(received_data)-3]
    #             break
        
    #     # decoding data received from server
    #     try:
    #         json_string = received_data.decode('utf-8')
    #         CONNECTIONS = json.loads(json_string)
    #     except:
    #         CONNECTIONS = dict()
    #         print("ERROR PICKLE TRUNCATED2")
    #     time.sleep(0.05)

# # main loop
# while True:
#     try:

#         # display every host in different cv frame
#         for host in CONNECTIONS.keys():
#             frame_data = np.frombuffer(base64.b64decode(CONNECTIONS[host].encode('utf-8')), 
#                                        dtype=np.uint8)
#             try:
#                 reconstructed_frame = cv.imdecode(frame_data, cv.IMREAD_COLOR)
#                 cv.imshow(str(host),reconstructed_frame)
#                 if cv.waitKey(1) == ord('q'):
#                     break
#             except:
#                 time.sleep(1)
                
#     except:
#         print("ERROR")