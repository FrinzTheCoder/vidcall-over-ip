import socket
import threading
import cv2 as cv

HOST = '192.168.0.2'
PORT = 19122
BUFFER_SIZE = 1048576
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    while True:
        client_socket, _ = server.accept()
        client_socket.sendall(frame_bytes)
        client_socket.close()
        
server_thread = threading.Thread(target=start_server)
server_thread.start()

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

    cv.imshow('frame', frame)
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()