import socket
import threading
import pickle

HOST = '192.168.0.2'
PORT = 19122
BUFFER_SIZE = 1048576
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

CONNECTIONS = dict()

# def send_thread(client_socket, data):
#     client_socket.sendall(data)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, 5000)  # 5-second receive timeout
    server.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, 5000)  # 5-second send timeout
    server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    server.listen(5)
    print("Server Online!")

    while True:
        client_socket, client_address = server.accept()
        print(str(client_address))
        client_address = client_address[0]
        print("accepting connection from: ", str(client_address))

        if client_address not in CONNECTIONS.keys():
            CONNECTIONS[client_address] = b''
        
        data = pickle.dumps(CONNECTIONS)
        # sending_thread = threading.Thread(target=send_thread,
        #                                   args=(client_socket, data))
        # sending_thread.start()
        client_socket.sendall(data)
        print("sending data")

        received_data = b''
        received_data = client_socket.recv(BUFFER_SIZE)
        # while True:
        #     print('a')
        #     data_chunk = client_socket.recv(BUFFER_SIZE)
        #     print('b')
        #     if not data_chunk:
        #         break
        #     received_data += data_chunk
        print("received data")
        client_socket.close()

        CONNECTIONS[client_address] = received_data
        
server_thread = threading.Thread(target=start_server)
server_thread.start()


# cap = cv.VideoCapture(0)
# cap.set(3, FRAME_WIDTH)
# cap.set(4, FRAME_HEIGHT)

# while True:
#     global frame_bytes
#     global frame
#     ret, frame = cap.read()
#     if not ret:
#         print("Error: Failed to capture frame.")
#         break
#     frame = cv.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
#     frame_bytes = cv.imencode('.jpg',frame)[1].tobytes()

#     cv.imshow('frame', frame)
#     if cv.waitKey(1) == ord('q'):
#         break

# cap.release()
# cv.destroyAllWindows()