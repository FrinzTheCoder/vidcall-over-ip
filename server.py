import socket
import threading
import json
import time
from codex import encode, decode
import cv2 as cv
import numpy as np

# DONT FORGET TO SET HOST AND PORT TO THE RIGHT VALUE
HOST = '192.168.1.3'
PORT = 19122
PORT_SENDER = 19124
PORT_RECEIVER = 19123
BUFFER_SIZE = 1048576
CONNECTIONS = dict()
IMAGES = dict()
PIN = '19122'

# SETUP THE TCP SERVER SOCKET
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server.bind((HOST, PORT))
server.listen(10)
print("Server Online!")

# SETUP THE CAMERA RECEIVER SOCKET
receiver_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# receiver_server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
receiver_server.bind((HOST, PORT_RECEIVER))
receiver_server.listen(10)
print("Receiver Server Online!")

# SETUP THE DISPLAY SENDER SOCKET
sender_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sender_server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sender_server.bind((HOST, PORT_SENDER))
sender_server.listen(10)
print("Sender Server Online!")

# handling for incoming connection by python client
def handle_connect_python(client_socket, client_address):
    global IMAGES
    while True:
        payload = client_socket.recv(BUFFER_SIZE) 
        type = 'IP_ADDR_INFO_RESPONSE'
        content =  [key for key in IMAGES.keys()]
        payload = encode(type, content)
        client_socket.send(payload)
    # while True:
    #     ip_address = client_address[0]
        
    #     # adding new host in connection in first connection
    #     if ip_address not in CONNECTIONS.keys():
    #         CONNECTIONS[ip_address] = ''
        
    #     while True:

    #         # receive incoming data until END flag found
            # received_data = b''
            # while True:
            #     data_chunk = client_socket.recv(BUFFER_SIZE)
            #     received_data += data_chunk
            #     if b'END' in received_data:
            #         received_data = received_data[:len(received_data)-3]
            #         break

    #         # send the entire images data to client
    #         json_string = json.dumps(CONNECTIONS)
    #         encoded_data = json_string.encode('utf-8')
    #         client_socket.sendall(encoded_data + b'END')
            
    #         try:
    #             # update the client images on the server side
    #             json_string = received_data.decode('utf-8')
    #             decoded_data = json.loads(json_string)
    #             CONNECTIONS[ip_address] = decoded_data['content']
    #         except:
    #             print("Error: Failure on updating client data")

    #         # add some delay
    #         time.sleep(0.05)

# handling for incoming connection from flutter client
def handle_connect_flutter(client_socket, client_addres):
    while True:
        # send the entire images data to client
        json_string = json.dumps(CONNECTIONS)
        encoded_data = json_string.encode('utf-8')
        client_socket.sendall(encoded_data)

        # add some delay
        time.sleep(0.05)

# decide whether the connection coming from python or flutter client
def handle_connect(client_socket, client_address):
    payload = client_socket.recv(BUFFER_SIZE)
    _ , content = decode(payload)
    
    # check whether the pin is valid or not
    type = 'CONNECTION_RESPONSE'
    if content != PIN:
        content = 'REJECTED'
        payload = encode(type, content)
        client_socket.send(payload)
        client_socket.close()
        return
    else:
        content = 'ACCEPTED'
        payload = encode(type, content)
        client_socket.send(payload)
        print("PIN Correct, Connection Accepted!")

    payload = client_socket.recv(BUFFER_SIZE)
    _, content = decode(payload)

    # check whether it is a Python or Flutter connection
    if content == 'Python':
        type = 'CONNECTION_SOURCE_RESPONSE'
        content = 'VALID'
        payload = encode(type, content)
        client_socket.send(payload)

        print(f"Serving {client_address[0]} as Python connection!")
        handle_connect_python(client_socket, client_address)
    elif content == 'Flutter':
        type = 'CONNECTION_SOURCE_RESPONSE'
        content = 'VALID'
        payload = encode(type, content)
        client_socket.send(payload)
        
        handle_connect_flutter(client_socket, client_address)
        print(f"Serving {client_address[0]} as Flutter connection!")
    else:
        type = 'CONNECTION_SOURCE_RESPONSE'
        content = 'INVALID'
        payload = encode(type, content)
        client_socket.send(payload)

        print("Error: Invalid connection type")
        client_socket.close()
        return

def receiver_threading_action(sender_socket, sender_address):
    global IMAGES
    while True:
        payload = sender_socket.recv(BUFFER_SIZE)
        type, _ =  decode(payload)
        if type == 'PUBLISH_REQUEST':
            IMAGES[sender_address[0]] = ''
            payload = encode('PUBLISH_RESPONSE','ACCEPTED')
            sender_socket.send(payload)
            time.sleep(0.5)
            while True:
                # check whether should stop or continue
                payload = sender_socket.recv(4)
                if payload == b'STOP':
                    print("BREAKING")
                    break
                sender_socket.send(b'ACK')

                # receiving the payload length
                payload_length = int(sender_socket.recv(20))
                sender_socket.send(b'ACK')

                # receiving payload
                payload = b''
                while len(payload) != payload_length:
                    payload += sender_socket.recv(1024)
                    sender_socket.send(b'ACK')
  
                # to be removed
                # frame_data = np.frombuffer(payload, dtype=np.uint8)
                # reconstructed_frame = cv.imdecode(frame_data, cv.IMREAD_COLOR)
                # cv.imshow('Coba', reconstructed_frame)
                # if cv.waitKey(1) == ord('q'):
                #     break
                
                # update the image
                IMAGES[sender_address[0]] = payload

                # time.sleep(0.05)
            del IMAGES[sender_address[0]]

def receiver_threading_entry_point():
    while True:
        sender_socket, sender_address = receiver_server.accept()
        print("accept camera connection:", sender_address[0])
        cam_threading_action_thread = threading.Thread(target=receiver_threading_action,
                                                       args=(sender_socket, sender_address))
        cam_threading_action_thread.start()

receiver_thread = threading.Thread(target=receiver_threading_entry_point)
receiver_thread.start()

def sender_threading_action(receiver_socket, receiver_address):
    global IMAGES
    while True:
        # receive the requested address
        address_requested = receiver_socket.recv(15)
        address_requested = address_requested.decode('utf-8')
        receiver_socket.send(b'ACK')

        # get the right data
        payload = IMAGES[address_requested]

        # send the data length
        receiver_socket.send(str(len(payload)).zfill(20).encode('utf-8'))
        receiver_socket.recv(3)

        # sending payload
        for i in range(0, len(payload), 1024):
            receiver_socket.send(payload[i:i+1024])
            receiver_socket.recv(3)
        
        # time.sleep(0.05)

def sender_threading_entry_point():
    while True:
        receiver_socket, receiver_address = sender_server.accept()
        print("request images from:", receiver_address[0])
        sender_threading_action_thread = threading.Thread(target=sender_threading_action,
                                                        args=(receiver_socket, receiver_thread))
        sender_threading_action_thread.start()

sender_thread = threading.Thread(target=sender_threading_entry_point)
sender_thread.start()


# main thread - to accept connection and execute commands
while True:
    client_socket, client_address = server.accept()
    print("accept connection:", client_address[0])
    client_thread = threading.Thread(target=handle_connect,
                                     args=(client_socket, client_address))
    client_thread.start()