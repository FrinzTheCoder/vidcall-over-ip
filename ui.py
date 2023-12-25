import tkinter as tk
from scrollable_frame import ScrollableFrame
from functools import partial
from codex import encode, decode
import cv2 as cv
import base64
import time
import threading
from PIL import Image, ImageTk
import numpy as np

class UserInterface(tk.Tk):
    
    def __init__(self, root, user_socket, sender_socket, receiver_socket, info):
        self.root = root
        self.user_socket = user_socket
        self.sender_socket = sender_socket
        self.receiver_socket = receiver_socket
        self.camera_state = False
        self.current_target_display = ''
        self.display_status = False
        self.GENERAL_INFORMATION = info
        self.BUFFER_SIZE = info['BUFFER_SIZE']
        self.list_of_address = []

        self.root.title("New Protocol! Self-Hosted Smart Devices V-0.2a")

        # left screen frame
        self.frame_left_screen = tk.Frame(root, width=640, height=480, background='black')
        self.frame_left_screen.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # left screen image
        self.label_for_image = tk.Label(self.frame_left_screen, background='black', width=64, height=48)
        self.label_for_image.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # right screen frame
        self.frame_right_screen = tk.Frame(root, width=320, height=480, background='white')
        self.frame_right_screen.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # nagivation for list of ip addresses
        self.frame_address_navigation = ScrollableFrame(self.frame_right_screen, background='green')
        self.frame_address_navigation.pack(side=tk.TOP, expand=True, fill=tk.BOTH, anchor=tk.N)

        # contron panel frame
        self.frame_control_panel = tk.Frame(self.frame_right_screen, width=320, height=120, background='yellow')
        self.frame_control_panel.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, anchor=tk.S)

        # toggle display button
        self.button_toggle_display = tk.Button(self.frame_control_panel, width=15, height=5, background='blue', text="Toggle Display")
        self.button_toggle_display.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, anchor=tk.W)

        # refresh ip addresses button
        self.button_refresh = tk.Button(self.frame_control_panel, width=15, height=5, background='red', text="Refresh", command=self.ip_address_info)
        self.button_refresh.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, anchor=tk.W)

        # toggle self camera button
        self.button_toggle_camera = tk.Button(self.frame_control_panel, width=15, height=5, background='green', text="Toggle Camera", command=self.toggle_video)
        self.button_toggle_camera.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, anchor=tk.W)
        
    def ip_address_info(self):

        # requesting available IP Addresses
        type = 'IP_ADDR_INFO_REQUEST'
        content = ''
        payload = encode(type, content)
        self.user_socket.send(payload)

        payload = self.user_socket.recv(self.BUFFER_SIZE)
        type, content = decode(payload)

        for item in self.list_of_address:
            item.destroy()

        for item in content:
            button = tk.Button(self.frame_address_navigation.frame, width=40, height=5, background='yellow', text=item)
            button.config(command=partial(self.set_video_target, item))
            button.pack(side=tk.TOP, expand=True, fill=tk.X, anchor=tk.N)
            self.list_of_address.append(button)

    def get_video(self):
        # declaring the target
        self.receiver_socket.send(self.current_target_display.encode('utf-8'))
        self.receiver_socket.recv(3)
        
        # receiving the payload length
        payload_length = int(self.receiver_socket.recv(20))
        self.receiver_socket.send(b'ACK')

        # receiving payload
        payload = b''
        while len(payload) != payload_length:
            payload += self.receiver_socket.recv(1024)
            self.receiver_socket.send(b'ACK')
        
        # decoding the payload
        frame_data = np.frombuffer(payload, dtype=np.uint8)
        reconstructed_frame = cv.imdecode(frame_data, cv.IMREAD_COLOR)
        rgb_frame = cv.cvtColor(reconstructed_frame, cv.COLOR_BGR2RGB)
        rgb_frame = cv.resize(rgb_frame, (640, 480))

        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img)

        self.label_for_image.imgtk = imgtk
        self.label_for_image.config(image=imgtk)

        if self.current_target_display != '':
            self.label_for_image.after(50, self.get_video)

    def set_video_target(self, address):
        if self.current_target_display == '':
            self.current_target_display = address
            self.receive_video_threading = threading.Thread(target=self.get_video)
            self.receive_video_threading.start()
        elif self.current_target_display != address:
            temp = address
            self.current_target_display = ''
            self.receive_video_threading.join()
            self.current_target_display = temp
            self.receive_video_threading = threading.Thread(target=self.get_video)
            self.receive_video_threading.start()

    def toggle_video(self):
        self.button_toggle_camera.config(state=tk.DISABLED)
        if self.camera_state == False:
            self.camera_state = True
            
            # setup the thread
            self.camera_thread = threading.Thread(target=self.open_cam_request)
            self.camera_thread.start()

            # try:
                
            # except:
            #     self.camera_state = False
            #     print("TEST2")
            #     # todo: message error
        else:
            self.camera_state = False
            self.button_toggle_camera.config(state=tk.ACTIVE)
    
    def open_cam_request(self):
        # request for opening camera
        type = 'PUBLISH_REQUEST'
        content = ''
        payload = encode(type, content)
        self.sender_socket.send(payload)

        # receiving response
        payload = self.sender_socket.recv(self.BUFFER_SIZE)
        _, content = decode(payload)
        if content == 'ACCEPTED':
            self.loop_camera()
        else:
            raise Exception("OPENING CAMERA FAILED: SERVER REJECTING CONNECTION")

    def loop_camera(self):
        # setting up the camera
        cap = cv.VideoCapture(0)
        frame_width = self.GENERAL_INFORMATION['FRAME_WIDTH']
        frame_height = self.GENERAL_INFORMATION['FRAME_HEIGHT']
        compression_params = self.GENERAL_INFORMATION['COMPRESSION_PARAMS']
        cap.set(3, frame_width)
        cap.set(4, frame_height)

        # enable the open cam button again
        self.button_toggle_camera.config(state=tk.ACTIVE)

        # camera capture main loop
        while self.camera_state == True:
            ret, frame = cap.read()
            if not ret:
                raise("OPENING CAMERA FAILED: CAM ERROR")
            frame = cv.resize(frame, (frame_width, frame_height))
            frame_bytes = cv.imencode('.jpg', frame, compression_params)[1].tobytes()
            
            # commit to send data
            self.sender_socket.send(b'SEND')
            self.sender_socket.recv(3)

            # send the data length information:
            self.sender_socket.send(str(len(frame_bytes)).zfill(20).encode('utf-8'))
            self.sender_socket.recv(3)

            # sending payload
            for i in range(0, len(frame_bytes), 1024):
                self.sender_socket.send(frame_bytes[i:i+1024])
                self.sender_socket.recv(3)

            if cv.waitKey(1) == ord('q'):
                break
        
            # time.sleep(0.05)

        self.sender_socket.send(b'STOP')
        cap.release()