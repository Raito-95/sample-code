import tkinter as tk
from PIL import ImageGrab
import numpy as np
import cv2
import threading
import time
import keyboard

def is_red_hsv(pixel, hue_range=((0, 10), (160, 180)), sat_min=100, val_min=100):
    pixel_hsv = cv2.cvtColor(np.uint8([[pixel]]), cv2.COLOR_RGB2HSV)[0][0]
    h, s, v = pixel_hsv
    return ((hue_range[0][0] <= h <= hue_range[0][1]) or (hue_range[1][0] <= h <= hue_range[1][1])) and s >= sat_min and v >= val_min

def calculate_red_percentage(img_np):
    red_pixels = np.sum([is_red_hsv(pixel) for row in img_np for pixel in row])
    total_pixels = img_np.shape[0] * img_np.shape[1]
    return (red_pixels / total_pixels) * 100

class ScreenMonitor:
    def __init__(self, root):
        self.root = root

        self.root.title("Screen Monitor")
        self.root.geometry("300x200")
        self.root.configure(bg="#2e3f4f")

        frame = tk.Frame(root, bg="#2e3f4f")
        frame.pack(pady=20, padx=20, anchor="w")

        tk.Label(frame, text="Insert:", font=("Helvetica", 12), bg="#2e3f4f", fg="white").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="Select HP Area", font=("Helvetica", 12), bg="#2e3f4f", fg="white").grid(row=0, column=1, sticky="w")

        tk.Label(frame, text="Home:", font=("Helvetica", 12), bg="#2e3f4f", fg="white").grid(row=1, column=0, sticky="w")
        tk.Label(frame, text="Select Inventory Area", font=("Helvetica", 12), bg="#2e3f4f", fg="white").grid(row=1, column=1, sticky="w")

        tk.Label(frame, text="Delete:", font=("Helvetica", 12), bg="#2e3f4f", fg="white").grid(row=2, column=0, sticky="w")
        tk.Label(frame, text="Start Monitoring", font=("Helvetica", 12), bg="#2e3f4f", fg="white").grid(row=2, column=1, sticky="w")

        tk.Label(frame, text="End:", font=("Helvetica", 12), bg="#2e3f4f", fg="white").grid(row=3, column=0, sticky="w")
        tk.Label(frame, text="Stop Monitoring", font=("Helvetica", 12), bg="#2e3f4f", fg="white").grid(row=3, column=1, sticky="w")

        tk.Label(frame, text="Page Up:", font=("Helvetica", 12), bg="#2e3f4f", fg="white").grid(row=4, column=0, sticky="w")
        tk.Label(frame, text="Exit Program", font=("Helvetica", 12), bg="#2e3f4f", fg="white").grid(row=4, column=1, sticky="w")

        self.hp_area = None
        self.inventory_area = None
        self.monitoring_threads = []
        self.monitoring = False

        self.gem_templates = self.load_gem_templates()

        keyboard.add_hotkey('insert', self.select_hp_area)
        keyboard.add_hotkey('home', self.select_inventory_area)
        keyboard.add_hotkey('delete', self.start_monitoring)
        keyboard.add_hotkey('end', self.stop_monitoring)
        keyboard.add_hotkey('pageup', self.exit_program)

    def load_gem_templates(self):
        gem_templates = {}

        for i in range(1, 22):
            template = cv2.imread(f"./images/gem_template_{i}.png", cv2.IMREAD_UNCHANGED)
            if template is not None:
                if template.shape[2] == 4:
                    b, g, r, a = cv2.split(template)
                    alpha_mask = a / 255.0
                    b = (1 - alpha_mask) * 0 + alpha_mask * b
                    g = (1 - alpha_mask) * 0 + alpha_mask * g
                    r = (1 - alpha_mask) * 0 + alpha_mask * r
                    template = cv2.merge([b, g, r])
                template = template.astype(np.uint8)
                gem_templates[f"gem_{i}"] = template
            else:
                print(f"Error loading gem_template_{i}.png")
        return gem_templates

    def select_hp_area(self):
        self.bring_to_front()
        self.select_area('hp')

    def select_inventory_area(self):
        self.bring_to_front()
        self.select_area('inventory')

    def bring_to_front(self):
        self.root.attributes('-topmost', 1)
        self.root.attributes('-topmost', 0)

    def select_area(self, area_type):
        self.top = tk.Toplevel(self.root)
        self.top.attributes('-alpha', 0.3)
        self.top.attributes('-fullscreen', True)
        self.top.config(bg='white')
        self.canvas = tk.Canvas(self.top, cursor="cross", bg='gray', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", lambda event, a=area_type: self.start_select(event, a))
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_select)

    def start_select(self, event, area_type):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline='blue')
        self.area_type = area_type

    def on_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
            if self.area_type == 'inventory':
                self.draw_grid(self.start_x, self.start_y, event.x, event.y)

    def draw_grid(self, x1, y1, x2, y2):
        self.canvas.delete("grid")
        cols, rows = 10, 4
        cell_width = (x2 - x1) / cols
        cell_height = (y2 - y1) / rows

        for i in range(cols + 1):
            x = x1 + i * cell_width
            self.canvas.create_line(x, y1, x, y2, tag="grid", fill='red')

        for i in range(rows + 1):
            y = y1 + i * cell_height
            self.canvas.create_line(x1, y, x2, y, tag="grid", fill='red')

    def end_select(self, event):
        area = (min(self.start_x, event.x), min(self.start_y, event.y),
                max(self.start_x, event.x), max(self.start_y, event.y))
        if self.area_type == 'hp':
            self.hp_area = area
        elif self.area_type == 'inventory':
            self.inventory_area = area
        self.top.destroy()

    def start_monitoring(self):
        self.monitoring = True
        if self.hp_area:
            thread = threading.Thread(target=self.monitor_hp_area, args=(self.hp_area,))
            thread.start()
            self.monitoring_threads.append(thread)
        if self.inventory_area:
            thread = threading.Thread(target=self.monitor_inventory_area)
            thread.start()
            self.monitoring_threads.append(thread)

    def stop_monitoring(self):
        self.monitoring = False

    def monitor_hp_area(self, area):
        while self.monitoring:
            screenshot = ImageGrab.grab(bbox=area)
            img_np = np.array(screenshot)
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)  # Convert from RGB to BGR
            red_percentage = calculate_red_percentage(img_np)
            print(f"HP: {red_percentage:.1f}%")
            time.sleep(1)

    def monitor_inventory_area(self):
        slot_rows, slot_cols = 4, 10
        while self.monitoring:
            if self.inventory_area:
                screenshot = ImageGrab.grab(bbox=self.inventory_area)
                inventory_img = np.array(screenshot)
                inventory_img = cv2.cvtColor(inventory_img, cv2.COLOR_RGB2BGR)  # Convert from RGB to BGR
                self.check_inventory_slots(inventory_img, slot_rows, slot_cols)
            time.sleep(1)

    def check_inventory_slots(self, inventory_img, slot_rows, slot_cols):
        slot_width = inventory_img.shape[1] // slot_cols
        slot_height = inventory_img.shape[0] // slot_rows
        gem_percentages = []

        for row in range(slot_rows):
            for col in range(slot_cols):
                slot_x, slot_y = col * slot_width, row * slot_height
                slot_img = inventory_img[slot_y:slot_y + slot_height, slot_x:slot_x + slot_width]

                # Display the slot image with pause
                # self.show_slot_image(slot_img)

                gem_percentage = self.calculate_gem_percentage(slot_img, slot_width, slot_height)
                gem_percentages.append(f'{gem_percentage:.1f}%')

        # Print gem percentages 10 per line
        for i in range(0, len(gem_percentages), 10):
            print(" ".join(gem_percentages[i:i + 10]))
        print('----------------------------------------')

    def calculate_gem_percentage(self, slot_img, slot_width, slot_height):
        gem_percentage = 0

        # Convert slot_img to grayscale
        slot_img_gray = cv2.cvtColor(slot_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)

        for key, template in self.gem_templates.items():
            resized_template = cv2.resize(template, (slot_width, slot_height))
            template_gray = cv2.cvtColor(resized_template, cv2.COLOR_BGR2GRAY).astype(np.uint8)
            
            res = cv2.matchTemplate(slot_img_gray, template_gray, cv2.TM_CCOEFF_NORMED)

            threshold = 0.1
            loc = np.where(res >= threshold)
            if loc[0].size > 0:
                gem_percentage = max(gem_percentage, np.max(res) * 100)
        return gem_percentage

    def show_slot_image(self, slot_img):
        # Check if slot_img is already RGB
        if slot_img.shape[2] == 3:
            slot_img_rgb = slot_img
        else:
            slot_img_rgb = cv2.cvtColor(slot_img, cv2.COLOR_BGR2RGB)

        cv2.imshow('Slot Image', slot_img_rgb)
        key = cv2.waitKey(0)  # Pause until a key is pressed
        if key == ord('q'):  # Press 'q' to close the image display
            cv2.destroyWindow('Slot Image')

    def exit_program(self):
        self.monitoring = False
        for thread in self.monitoring_threads:
            thread.join()
        self.root.destroy()
        cv2.destroyAllWindows()  # Close all OpenCV windows

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenMonitor(root)
    app.run()
