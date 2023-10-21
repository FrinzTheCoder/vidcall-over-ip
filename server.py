import socket
import threading
import pickle

HOST = '192.168.0.2'
PORT = 19122
BUFFER_SIZE = 52428800

CONNECTIONS = dict()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    print("Server Online!")

    while True:
        message_addresss = server.recvfrom(BUFFER_SIZE)
        received_data = message_addresss[0]
        address = message_addresss[1]
        ip_address = address[0]

        if ip_address not in CONNECTIONS.keys():
            CONNECTIONS[ip_address] = b''
        
        data = pickle.dumps(CONNECTIONS)
        server.sendto(data, address)
        print("sent data to:", str(address))
        CONNECTIONS[ip_address] = received_data
        
server_thread = threading.Thread(target=start_server)
server_thread.start()
