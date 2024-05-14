import threading
from pynput import mouse, keyboard
import logging
from threading import Lock

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class MouseKeyboardControl:
    def __init__(self):
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.lock = Lock()
        self.actions = {
            'click_left': {'event': threading.Event(), 'method': self.click_left, 'interval': 0.2},
            'click_right': {'event': threading.Event(), 'method': self.click_right, 'interval': 0.6},
            'press_f8': {'event': threading.Event(), 'method': self.press_key, 'key': keyboard.Key.f8, 'interval': 10},
            'press_f7': {'event': threading.Event(), 'method': self.press_key, 'key': keyboard.Key.f7, 'interval': 1}
        }
        self.clicking_active = False

    def print_event_time(self, event_description):
        logging.info(event_description)

    def click_left(self):
        while not self.actions['click_left']['event'].is_set():
            with self.lock:
                self.mouse_controller.click(mouse.Button.left)
                self.print_event_time("Left mouse clicked")
            self.actions['click_left']['event'].wait(
                self.actions['click_left']['interval'])

    def click_right(self):
        while not self.actions['click_right']['event'].is_set():
            with self.lock:
                self.mouse_controller.click(mouse.Button.right)
                self.print_event_time("Right mouse clicked")
            self.actions['click_right']['event'].wait(
                self.actions['click_right']['interval'])

    def press_key(self, action_name):
        action = self.actions[action_name]
        while not action['event'].is_set():
            with self.lock:
                self.keyboard_controller.press(action['key'])
                self.keyboard_controller.release(action['key'])
                self.print_event_time(f"{action['key']} key pressed")
            action['event'].wait(action['interval'])

    def on_press(self, key):
        try:
            if key == keyboard.Key.delete and not self.clicking_active:
                for action in self.actions.values():
                    action['event'].clear()
                self.clicking_active = True
                for name, action in self.actions.items():
                    threading.Thread(target=action['method'], args=(
                        name,) if 'press_' in name else ()).start()
                self.keyboard_controller.press(keyboard.Key.ctrl)
                self.print_event_time("Delete pressed and actions started")
            elif key == keyboard.Key.end:
                self.stop_actions()
            elif key == keyboard.Key.page_down:
                self.exit_program()
        except Exception as e:
            self.print_event_time(f"Exception in on_press: {str(e)}")

    def on_release(self, key):
        self.print_event_time(f"Key released: {key}")

    def stop_actions(self):
        for action in self.actions.values():
            action['event'].set()
        self.clicking_active = False
        self.keyboard_controller.release(keyboard.Key.ctrl)
        self.print_event_time("End pressed and actions stopped")

    def exit_program(self):
        self.stop_actions()
        self.print_event_time("Exiting program gracefully")
        raise SystemExit

    def start_listening(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


if __name__ == "__main__":
    controller = MouseKeyboardControl()
    controller.start_listening()
