import socket
import threading
import cv2 as cv

HOST = '192.168.0.2'
PORT = 19122
BUFFER_SIZE = 1048576
FRAME_WIDTH = 200
FRAME_HEIGHT = 200

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))

    while True:
        try:
            message_address = server.recvfrom(BUFFER_SIZE)
            message = message_address[0]
            address = message_address[1]
            
            print(frame)
            server.sendto(frame_bytes, address)
        except KeyboardInterrupt:
            break

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