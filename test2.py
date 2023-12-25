import tkinter as tk

class ScrollableFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        
        # Create a canvas
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Set the scroll region to encompass the inner frame"""
        width = event.width
        self.canvas.itemconfig(self.frame, width=width)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scrollable Frame Example")

    scrollable_frame = ScrollableFrame(root)
    scrollable_frame.pack(side="top", fill="both", expand=True)

    # Add some widgets to the scrollable frame
    for i in range(50):
        label = tk.Label(scrollable_frame.frame, text=f"Label {i}")
        label.pack(pady=10)

    root.mainloop()
