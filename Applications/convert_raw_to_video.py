import os
import numpy as np
import cv2
from tkinter import Tk, filedialog, messagebox

# Disable the default GUI window from Tkinter
Tk().withdraw()

# Open file dialog
raw_file = filedialog.askopenfilename(
    title="Select a .raw file",
    filetypes=[("RAW files", "*.raw")]
)

if not raw_file:
    messagebox.showerror("Error", "No file selected. Exiting program.")
    exit()

output_video = os.path.splitext(raw_file)[0] + ".mp4"

# Image parameters
width, height = 2560, 720
pixel_format = 'GRAY8'
fps = 30

if pixel_format == 'GRAY8':
    dtype = np.uint8
    pixel_size = 1
elif pixel_format == 'GRAY16':
    dtype = np.uint16
    pixel_size = 2
else:
    messagebox.showerror("Error", "Unsupported pixel format")
    exit()

frame_size = width * height * pixel_size
file_size = os.path.getsize(raw_file)

if file_size % frame_size != 0:
    messagebox.showerror("Error", f"File size {file_size} bytes is not divisible by frame size {frame_size}")
    exit()

num_frames = file_size // frame_size

# Setup video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height), isColor=False)

# Read frame-by-frame directly from file
with open(raw_file, "rb") as f:
    for i in range(num_frames):
        frame_data = f.read(frame_size)
        if len(frame_data) != frame_size:
            messagebox.showerror("Error", f"Incomplete frame at index {i}")
            break

        frame = np.frombuffer(frame_data, dtype=dtype).reshape((height, width))

        if pixel_format == 'GRAY16':
            frame = (frame / 16).astype(np.uint8)

        video_writer.write(frame)

video_writer.release()
messagebox.showinfo("Success", f"Video has been saved to: {output_video}")
