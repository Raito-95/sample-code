import sys
import time
import threading
from pynput import keyboard
from pynput.keyboard import Listener as KeyboardListener, Controller as KeyboardController
from pynput.mouse import Listener as MouseListener, Controller as MouseController

class ActionRecorder:
    def __init__(self):
        self.recording = False
        self.playing = False
        self.events = []
        self.keyboard_listener = KeyboardListener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener = MouseListener(on_move=self.on_move, on_click=self.on_click)
        self.keyboard_controller = KeyboardController()
        self.mouse_controller = MouseController()
        self.last_event_time = None

    def on_press(self, key):
        if hasattr(key, 'char'):
            if key.char == '\x12':  # Ctrl+R
                if not self.recording and not self.playing:
                    self.recording = True
                    self.events = []
                    self.last_event_time = time.time()
                    print("Start recording...")
                    return
                elif self.recording:
                    self.recording = False
                    print("Recording ended...")
                    return
            if key.char == '\x10':  # Ctrl+P
                if not self.playing:
                    self.playing = True
                    print("Start playback...")
                    threading.Thread(target=self.play_events).start()
                    return
                elif self.playing:
                    self.playing = False
                    print("Playback stopped...")
                    return
            if key.char == '\x11':  # Ctrl+Q
                print("Exiting program...")
                self.keyboard_listener.stop()
                self.mouse_listener.stop()
                sys.exit(0)

        if self.recording:
            now = time.time()
            if self.last_event_time is None:
                self.last_event_time = now
            self.events.append({
                'type': 'key',
                'key': key,
                'delay': now - self.last_event_time
            })
            self.last_event_time = now
            print(f"Recorded keyboard key: {key}")

    def on_release(self, key):
        pass

    def on_move(self, x, y):
        if self.recording:
            now = time.time()
            if self.last_event_time is None:
                self.last_event_time = now
            self.events.append({
                'type': 'move',
                'x': x,
                'y': y,
                'delay': now - self.last_event_time
            })
            self.last_event_time = now
            print(f"Recorded mouse movement to ({x}, {y})")

    def on_click(self, x, y, button, pressed):
        if self.recording:
            now = time.time()
            if self.last_event_time is None:
                self.last_event_time = now
            self.events.append({
                'type': 'click',
                'x': x,
                'y': y,
                'button': button,
                'pressed': pressed,
                'delay': now - self.last_event_time
            })
            self.last_event_time = now
            print(f"Recorded mouse click: {'Pressed' if pressed else 'Released'} at ({x}, {y})")

    def play_events(self):
        while self.playing:
            for event in self.events:
                if not self.playing:
                    break
                time.sleep(event['delay'])
                event_type = event['type']
                if event_type == 'key':
                    key = event['key']
                    if isinstance(key, keyboard.KeyCode):
                        key = key.char
                    print(f"Playing keyboard key: {key}")
                    self.keyboard_controller.press(key)
                    self.keyboard_controller.release(key)
                elif event_type == 'move':
                    x, y = event['x'], event['y']
                    print(f"Playing mouse movement to ({x}, {y})")
                    self.mouse_controller.position = (x, y)
                elif event_type == 'click':
                    x, y, button, pressed = event['x'], event['y'], event['button'], event['pressed']
                    print(f"Playing mouse click: {'Pressed' if pressed else 'Released'} at ({x}, {y})")
                    self.mouse_controller.position = (x, y)
                    if pressed:
                        self.mouse_controller.press(button)
                    else:
                        self.mouse_controller.release(button)
            time.sleep(1)

if __name__ == '__main__':
    recorder = ActionRecorder()
    with recorder.keyboard_listener, recorder.mouse_listener:
        recorder.keyboard_listener.join()
        recorder.mouse_listener.join()
