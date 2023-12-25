import cv2
import tkinter as tk
from PIL import Image, ImageTk

def update_frame():
    # Capture a frame from the camera
    ret, frame = cap.read()

    # Convert the frame from BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert the frame to ImageTk format
    img = Image.fromarray(rgb_frame)
    imgtk = ImageTk.PhotoImage(image=img)

    # Update the label with the new image
    label.imgtk = imgtk
    label.config(image=imgtk)

    # Call the function again after a delay (e.g., 10 ms)
    label.after(10, update_frame)

# Open the video capture device (e.g., the default camera)
cap = cv2.VideoCapture(0)  # Use 0 for the default camera. Adjust if necessary.

# Create a Tkinter window
root = tk.Tk()
root.title("OpenCV and Tkinter Integration")

# Create a label widget to display the frame
label = tk.Label(root)
label.pack(padx=10, pady=10)

# Start updating the frame
update_frame()

# Run the Tkinter event loop
root.mainloop()

# Release the video capture and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()
