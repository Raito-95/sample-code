import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageGrab
import numpy as np
import cv2
import pyautogui


class ScreenRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Recorder")
        self.root.geometry("250x250")
        self.root.configure(bg="#f0f0f0")

        button_font = ("Arial", 12)
        button_bg = "#e0e0e0"
        button_fg = "#333333"

        self.select_area_button = tk.Button(root, text="Select Recording Area", command=self.start_select_area,
                                            font=button_font, bg=button_bg, fg=button_fg)
        self.select_area_button.pack(pady=10)

        self.start_button = tk.Button(root, text="Start Recording", command=self.start_recording,
                                      font=button_font, bg=button_bg, fg=button_fg, state=tk.DISABLED)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Recording", command=self.stop_recording,
                                     font=button_font, bg=button_bg, fg=button_fg, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.exit_button = tk.Button(root, text="Exit Program", command=self.exit_program,
                                     font=button_font, bg=button_bg, fg=button_fg)
        self.exit_button.pack(pady=10)

        self.recording_status = tk.Label(
            root, text="Status: Not Recording", bg="#f0f0f0", fg="#333333")
        self.recording_status.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_program)
        self.root.after(10, self.update)

        self.rect = None
        self.video_writer = None
        self.recording = False

    def start_select_area(self):
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.5)
        self.selection_window.wm_attributes("-topmost", 1)
        self.selection_canvas = tk.Canvas(self.selection_window)
        self.selection_canvas.pack(fill="both", expand=True)
        self.selection_window.bind("<Button-1>", self.on_mouse_down)
        self.rect_id = None
        self.rect = None

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.selection_window.bind("<B1-Motion>", self.on_mouse_drag)
        self.selection_window.bind("<ButtonRelease-1>", self.on_mouse_release)

    def on_mouse_drag(self, event):
        self.rect = (self.start_x, self.start_y, event.x, event.y)
        self.draw_rectangle()

    def on_mouse_release(self, event):
        self.selection_window.unbind("<B1-Motion>")
        self.selection_window.unbind("<ButtonRelease-1>")
        self.selection_window.destroy()
        self.start_button.config(state=tk.NORMAL)

    def draw_rectangle(self):
        if self.rect_id:
            self.selection_canvas.delete(self.rect_id)

        if self.rect and len(self.rect) == 4:
            normalized_rect = (
                min(self.rect[0], self.rect[2]),
                min(self.rect[1], self.rect[3]),
                max(self.rect[0], self.rect[2]),
                max(self.rect[1], self.rect[3])
            )
            self.rect_id = self.selection_canvas.create_rectangle(
                normalized_rect, outline="red", width=5)
        else:
            print("Rectangle coordinates are not set properly.")

    def start_recording(self):
        if self.rect is None:
            messagebox.showwarning(
                "Warning", "Please select recording area before starting recording.")
            return

        if len(self.rect) != 4 or not all(isinstance(n, int) for n in self.rect):
            messagebox.showwarning(
                "Warning", "Recording area is not set correctly.")
            return

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        temp_filename = "temp_screen_capture.avi"
        self.video_writer = cv2.VideoWriter(
            temp_filename, fourcc, 30.0, (self.rect[2] - self.rect[0], self.rect[3] - self.rect[1]))

        self.recording = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.select_area_button.config(state=tk.DISABLED)
        self.recording_status.config(text="Status: Recording")

    def stop_recording(self):
        self.recording = False
        self.video_writer.release()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.select_area_button.config(state=tk.NORMAL)
        self.recording_status.config(text="Status: Not Recording")

        save_path = filedialog.asksaveasfilename(
            defaultextension=".avi", filetypes=[("AVI files", "*.avi")])
        if save_path:
            os.rename("temp_screen_capture.avi", save_path)
            messagebox.showinfo("Info", f"Recording saved to: {save_path}")
        else:
            os.remove("temp_screen_capture.avi")
            messagebox.showinfo("Info", "Recording discarded.")

    def update(self):
        if self.recording and self.rect is not None:
            screenshot = ImageGrab.grab(bbox=self.rect)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mouse_x, mouse_y = pyautogui.position()
            if self.rect[0] <= mouse_x <= self.rect[2] and self.rect[1] <= mouse_y <= self.rect[3]:
                center_x = int(mouse_x - self.rect[0])
                center_y = int(mouse_y - self.rect[1])
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

            self.video_writer.write(frame)

        self.root.after(10, self.update)

    def run(self):
        self.root.mainloop()

    def exit_program(self):
        if self.recording:
            messagebox.showwarning(
                "Warning", "Please stop the recording before exiting the program.")
            return

        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorderApp(root)
    app.run()
