import socket
import threading
import pickle
import time

HOST = '192.168.0.2'
PORT = 19122
BUFFER_SIZE = 20480

CONNECTIONS = dict()
BUFFER = dict()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    server.bind((HOST, PORT))
    print("Server Online!")

    while True:
        message_addresss = server.recvfrom(BUFFER_SIZE+100000)
        received_data = message_addresss[0]
        address = message_addresss[1]
        ip_address = address[0]

        if ip_address not in CONNECTIONS.keys():
            CONNECTIONS[ip_address] = b''
            BUFFER[ip_address] = b''

        if received_data == b'END':
            CONNECTIONS[ip_address] = BUFFER[ip_address]
            BUFFER[ip_address] = b''
            
            data = pickle.dumps(CONNECTIONS)
            chunks = [data[i:i+BUFFER_SIZE] for i in range(0, len(data), BUFFER_SIZE)]
            for chunk in chunks:
                time.sleep(0.1)
                server.sendto(chunk, address)
            server.sendto(b'END', address)
            print("sent data to:", str(address))
        else:
            BUFFER[ip_address] = BUFFER[ip_address] + received_data
        
server_thread = threading.Thread(target=start_server)
server_thread.start()
