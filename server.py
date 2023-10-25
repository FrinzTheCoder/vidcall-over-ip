import socket
import threading
import json
import time

# DONT FORGET TO SET HOST AND PORT TO THE RIGHT VALUE
HOST = '192.168.1.4'
PORT = 19122
BUFFER_SIZE = 1048576
CONNECTIONS = dict()

# SETUP THE TCP SERVER SOCKET
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server.bind((HOST, PORT))
server.listen(5)
print("Server Online!")

# handling for incoming connection by python client
def handle_connect_python(client_socket, client_address):
    while True:
        ip_address = client_address[0]
        
        if ip_address not in CONNECTIONS.keys():
            CONNECTIONS[ip_address] = ''
        
        while True:
            received_data = b''
            print("listening...")
            while True:
                data_chunk = client_socket.recv(BUFFER_SIZE)
                received_data += data_chunk
                print(received_data)
                if b'END' in received_data:
                    received_data = received_data[:len(received_data)-3]
                    break
            json_string = json.dumps(CONNECTIONS)
            encoded_data = json_string.encode('utf-8')
            client_socket.sendall(encoded_data + b'END')
            
            if b'FLUTTER' not in received_data:
                json_string = received_data.decode('utf-8')
                decoded_data = json.loads(json_string)
                CONNECTIONS[ip_address] = decoded_data['content']
            time.sleep(0.05)

# handling for incoming connection from flutter client
def handle_connect_flutter(client_socket, client_addres):
    pass

# decide whether the connection coming from python or flutter client
def handle_connect(client_socket, client_address):
    type = client_socket.recv(BUFFER_SIZE)

    # P for Python
    if type == b'P': 
        handle_connect_python(client_socket, client_address)
    # F for Flutter
    if type == b'F':
        handle_connect_flutter(client_socket, client_address)
    else:
        print("Error: Invalid connection")
        exit()

# main module - accepting incoming request and make
# new thread to serve each of incoming request
while True:
    client_socket, client_address = server.accept()
    print("accept connection:", client_address[0])
    client_thread = threading.Thread(target=handle_connect,
                                     args=(client_socket, client_address))
    client_thread.start()