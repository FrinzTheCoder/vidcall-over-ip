import socket
import threading
import pickle
import time

HOST = '192.168.0.2'
PORT = 19122
BUFFER_SIZE = 204800

CONNECTIONS = dict()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print("Server Online!")

    while True:
        client_socket, client_address = server.accept()
        ip_address = client_address[0]
        print("accept connection:",ip_address)
        
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

server_thread = threading.Thread(target=start_server)
server_thread.start()
