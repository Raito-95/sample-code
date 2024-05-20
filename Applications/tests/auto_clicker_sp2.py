import tkinter as tk
from PIL import ImageGrab
import numpy as np
import cv2
import threading
import keyboard
import pyautogui
import time
from typing import Tuple, Dict, List, Optional

HUE_RANGE = ((0, 10), (160, 180))
SAT_MIN = 100
VAL_MIN = 100
HIST_SIZE = [8, 8, 8]
HIST_RANGE = [0, 256, 0, 256, 0, 256]


def calculate_red_percentage(img_np: np.ndarray) -> float:
    img_hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([HUE_RANGE[0][0], SAT_MIN, VAL_MIN])
    upper_red1 = np.array([HUE_RANGE[0][1], 255, 255])
    lower_red2 = np.array([HUE_RANGE[1][0], SAT_MIN, VAL_MIN])
    upper_red2 = np.array([HUE_RANGE[1][1], 255, 255])

    mask1 = cv2.inRange(img_hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(img_hsv, lower_red2, upper_red2)
    mask = np.bitwise_or(mask1, mask2)

    red_pixels = np.sum(mask > 0)
    total_pixels = img_np.shape[0] * img_np.shape[1]
    return float((red_pixels / total_pixels) * 100)


class ScreenMonitor:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Screen Monitor")
        self.root.geometry("300x200")
        self.root.configure(bg="#2e3f4f")

        self.slot_rows = 4
        self.slot_cols = 10
        self.monitoring = False
        self.monitoring_threads: List[threading.Thread] = []
        self.hp_area: Optional[Tuple[int, int, int, int]] = None
        self.inventory_area: Optional[Tuple[int, int, int, int]] = None
        self.ore_templates = self.load_ore_templates()
        self.selection_window = None

        self.create_ui()
        self.setup_keyboard_shortcuts()

    def create_ui(self):
        frame = tk.Frame(self.root, bg="#2e3f4f")
        frame.pack(pady=20, padx=20, anchor="w")

        labels = [
            ("Insert:", "Select HP Area"),
            ("Home:", "Select Inventory Area"),
            ("Delete:", "Start Monitoring"),
            ("End:", "Stop Monitoring"),
            ("Page Up:", "Exit Program"),
        ]

        for i, (label1, label2) in enumerate(labels):
            tk.Label(
                frame, text=label1, font=("Helvetica", 12), bg="#2e3f4f", fg="white"
            ).grid(row=i, column=0, sticky="w")
            tk.Label(
                frame, text=label2, font=("Helvetica", 12), bg="#2e3f4f", fg="white"
            ).grid(row=i, column=1, sticky="w")

    def setup_keyboard_shortcuts(self):
        keyboard.add_hotkey("insert", self.select_hp_area)
        keyboard.add_hotkey("home", self.select_inventory_area)
        keyboard.add_hotkey("delete", self.start_monitoring)
        keyboard.add_hotkey("end", self.stop_monitoring)
        keyboard.add_hotkey("pageup", self.exit_program)

    def load_ore_templates(self) -> Dict[str, np.ndarray]:
        ore_templates = {}
        ores = ["iron_ore", "copper_ore", "gold_ore"]

        for ore in ores:
            try:
                template = cv2.imread(f"./images/{ore}.png", cv2.IMREAD_COLOR)
                if template is not None:
                    ore_templates[ore] = template
                    print(f"Loaded template for {ore}.")
                else:
                    print(f"Error loading {ore}.png")
            except Exception as e:
                print(f"Exception loading {ore}.png: {e}")
        return ore_templates

    def select_hp_area(self):
        self.bring_to_front()
        self.select_area("hp")

    def select_inventory_area(self):
        self.bring_to_front()
        self.select_area("inventory")

    def bring_to_front(self):
        self.root.attributes("-topmost", 1)
        self.root.attributes("-topmost", 0)

    def select_area(self, area_type: str):
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes("-fullscreen", True)
        self.selection_window.attributes("-topmost", True)
        self.selection_window.overrideredirect(True)
        self.selection_window.attributes("-alpha", 0.3)
        self.selection_window.configure(bg="gray")

        self.canvas = tk.Canvas(
            self.selection_window, cursor="cross", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind(
            "<ButtonPress-1>", lambda event, a=area_type: self.start_select(event, a)
        )
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_select)

    def start_select(self, event: tk.Event, area_type: str):
        self.start_x, self.start_y = event.x, event.y
        self.area_type = area_type
        outline_color = "blue" if self.area_type == "hp" else "red"
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline=outline_color, width=3
        )

    def on_drag(self, event: tk.Event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        if self.area_type == "inventory":
            self.canvas.delete("grid")
            self.draw_grid(self.start_x, self.start_y, event.x, event.y)

    def draw_grid(self, x1: int, y1: int, x2: int, y2: int):
        cell_width = (x2 - x1) / self.slot_cols
        cell_height = (y2 - y1) / self.slot_rows

        for i in range(self.slot_cols + 1):
            x = int(x1 + i * cell_width)
            self.canvas.create_line(x, y1, x, y2, tags="grid", fill="red", width=3)

        for i in range(self.slot_rows + 1):
            y = int(y1 + i * cell_height)
            self.canvas.create_line(x1, y, x2, y, tags="grid", fill="red", width=3)

    def end_select(self, event: tk.Event):
        area = (
            min(self.start_x, event.x),
            min(self.start_y, event.y),
            max(self.start_x, event.x),
            max(self.start_y, event.y),
        )
        if self.area_type == "hp":
            self.hp_area = area
        elif self.area_type == "inventory":
            self.inventory_area = area
        self.stop_selection()

    def stop_selection(self):
        if self.selection_window:
            self.selection_window.destroy()
            self.selection_window = None

    def start_monitoring(self):
        self.monitoring = True
        if self.hp_area:
            thread = threading.Thread(target=self.monitor_hp_area)
            thread.start()
            self.monitoring_threads.append(thread)
        if self.inventory_area:
            thread = threading.Thread(target=self.monitor_inventory_area)
            thread.start()
            self.monitoring_threads.append(thread)

    def stop_monitoring(self):
        self.monitoring = False

    def monitor_hp_area(self):
        while self.monitoring:
            screenshot = ImageGrab.grab(bbox=self.hp_area)
            img_np = np.array(screenshot)
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            red_percentage = calculate_red_percentage(img_np)
            print(f"HP: {red_percentage:.1f}%")
            time.sleep(1)

    def monitor_inventory_area(self):
        while self.monitoring:
            screenshot = ImageGrab.grab(bbox=self.inventory_area)
            inventory_img = np.array(screenshot)
            inventory_img = cv2.cvtColor(inventory_img, cv2.COLOR_RGB2BGR)
            self.check_inventory_slots(inventory_img)
            time.sleep(1)

    def check_inventory_slots(self, inventory_img: np.ndarray):
        slot_width = inventory_img.shape[1] // self.slot_cols
        slot_height = inventory_img.shape[0] // self.slot_rows

        for row in range(self.slot_rows):
            for col in range(self.slot_cols):
                slot_x, slot_y = col * slot_width, row * slot_height
                slot_img = inventory_img[
                    slot_y : slot_y + slot_height, slot_x : slot_x + slot_width
                ]

                ore_percentage, ore_type = self.calculate_ore_percentage(
                    slot_img, slot_width, slot_height
                )
                print(
                    f"Slot [{row + 1}, {col + 1}] - {ore_type}: {ore_percentage:.1f}%"
                )

                if ore_percentage >= 90:
                    self.discard_ore(slot_x, slot_y, slot_width, slot_height)
                    return

    def calculate_ore_percentage(
        self, slot_img: np.ndarray, slot_width: int, slot_height: int
    ) -> Tuple[float, str]:
        best_match = max(
            (
                (
                    self.compare_histograms(
                        slot_img, template, slot_width, slot_height
                    ),
                    key,
                )
                for key, template in self.ore_templates.items()
            ),
            key=lambda x: x[0],
        )
        return best_match[0] * 100, best_match[1]

    def compare_histograms(
        self,
        slot_img: np.ndarray,
        template: np.ndarray,
        slot_width: int,
        slot_height: int,
    ) -> float:
        resized_template = cv2.resize(template, (slot_width, slot_height))

        slot_hist = cv2.calcHist([slot_img], [0, 1, 2], None, HIST_SIZE, HIST_RANGE)
        template_hist = cv2.calcHist(
            [resized_template], [0, 1, 2], None, HIST_SIZE, HIST_RANGE
        )

        cv2.normalize(slot_hist, slot_hist)
        cv2.normalize(template_hist, template_hist)

        similarity = cv2.compareHist(slot_hist, template_hist, cv2.HISTCMP_CORREL)
        return similarity

    def discard_ore(self, slot_x: int, slot_y: int, slot_width: int, slot_height: int):
        if self.inventory_area is None:
            return
        
        inventory_top_left = self.inventory_area[0:2]
        slot_center_x = inventory_top_left[0] + slot_x + slot_width // 2
        slot_center_y = inventory_top_left[1] + slot_y + slot_height // 2

        pyautogui.moveTo(slot_center_x, slot_center_y)
        pyautogui.dragTo(inventory_top_left[0] - 100, slot_center_y, duration=0.5)

    def exit_program(self):
        self.monitoring = False
        for thread in self.monitoring_threads:
            thread.join()
        self.root.destroy()
        cv2.destroyAllWindows()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenMonitor(root)
    app.run()
