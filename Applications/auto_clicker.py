import threading
from pynput import mouse, keyboard
from datetime import datetime
from threading import Lock

class MouseKeyboardControl:
    def __init__(self):
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.stop_clicking_left = threading.Event()
        self.stop_clicking_right = threading.Event()
        self.stop_key_press = threading.Event()
        self.lock = Lock()
        self.clicking_active = False
        self.timer = None

    def print_event_time(self, event_description):
        print(f"{event_description} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def click_left(self):
        while not self.stop_clicking_left.is_set():
            with self.lock:
                self.mouse_controller.click(mouse.Button.left)
                self.print_event_time("Left mouse clicked")
            self.stop_clicking_left.wait(0.2)

    def click_right(self):
        while not self.stop_clicking_right.is_set():
            with self.lock:
                self.mouse_controller.click(mouse.Button.right)
                self.print_event_time("Right mouse clicked")
            self.stop_clicking_right.wait(1)

    def press_key(self):
        while not self.stop_key_press.is_set():
            with self.lock:
                self.keyboard_controller.press(keyboard.Key.f10)
                self.keyboard_controller.release(keyboard.Key.f10)
                self.print_event_time("F10 key pressed")
                self.keyboard_controller.press(keyboard.Key.f9)
                self.keyboard_controller.release(keyboard.Key.f9)
                self.print_event_time("F9 key pressed")
            self.stop_key_press.wait(10)

    def on_press(self, key):
        if hasattr(key, 'char') and key.char is not None:
            if key.char == 'z' and not self.clicking_active:
                self.stop_clicking_left.clear()
                self.stop_clicking_right.clear()
                self.stop_key_press.clear()
                self.clicking_active = True
                threading.Thread(target=self.click_left).start()
                threading.Thread(target=self.click_right).start()
                threading.Thread(target=self.press_key).start()
                self.keyboard_controller.press(keyboard.Key.ctrl)
                self.print_event_time("Ctrl pressed and mouse clicking started")
            elif key.char == 'x' or key.char == '\x18':
                self.stop_clicking_left.set()
                self.stop_clicking_right.set()
                self.stop_key_press.set()
                self.clicking_active = False
                self.keyboard_controller.release(keyboard.Key.ctrl)
                self.print_event_time("Ctrl released and mouse clicking stopped")
            elif key.char == 'q' or key.char == '\x11':
                self.stop_clicking_left.set()
                self.stop_clicking_right.set()
                self.stop_key_press.set()
                if self.clicking_active:
                    self.keyboard_controller.release(keyboard.Key.ctrl)
                self.clicking_active = False
                self.print_event_time("Exiting program")
                return False

    def on_release(self, key):
        self.print_event_time(f"Key released: {key}")

    def start_listening(self):
        try:
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                listener.join()
        except Exception as e:
            self.print_event_time(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    controller = MouseKeyboardControl()
    controller.start_listening()
