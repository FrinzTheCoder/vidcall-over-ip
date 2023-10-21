import socket
import threading
import pickle
import time

HOST = '192.168.0.2'
PORT = 19122
BUFFER_SIZE = 1048576

CONNECTIONS = dict()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server.bind((HOST, PORT))
server.listen(5)
print("Server Online!")

def handle_connect(client_socket, client_address):
    while True:
        ip_address = client_address[0]
        
        if ip_address not in CONNECTIONS.keys():
            CONNECTIONS[ip_address] = b''
        
        while True:
            received_data = b''
            while True:
                data_chunk = client_socket.recv(BUFFER_SIZE)
                received_data += data_chunk
                if b'END' in received_data:
                    received_data = received_data[:len(received_data)-3]
                    break
            
            data = pickle.dumps(CONNECTIONS)
            client_socket.sendall(data+b'END')
            CONNECTIONS[ip_address] = received_data
            time.sleep(0.1)

while True:
    client_socket, client_address = server.accept()
    print("accept connection:", client_address[0])
    client_thread = threading.Thread(target=handle_connect,
                                     args=(client_socket, client_address))
    client_thread.start()