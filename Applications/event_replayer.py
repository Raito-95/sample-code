import sys
import json
import time
import threading
from collections import namedtuple
from queue import Queue, Empty
from tkinter import filedialog
import tkinter as tk

from pynput import keyboard
from pynput.keyboard import Listener as KeyboardListener, Controller as KeyboardController, Key, KeyCode
from pynput.mouse import Listener as MouseListener, Controller as MouseController, Button



ComboKeys = namedtuple('ComboKeys', ['ctrl_a', 'ctrl_b', 'ctrl_c', 'ctrl_d', 'ctrl_e',
                                     'ctrl_f', 'ctrl_g', 'ctrl_h', 'ctrl_i', 'ctrl_j',
                                     'ctrl_k', 'ctrl_l', 'ctrl_m', 'ctrl_n', 'ctrl_o',
                                     'ctrl_p', 'ctrl_q', 'ctrl_r', 'ctrl_s', 'ctrl_t',
                                     'ctrl_u', 'ctrl_v', 'ctrl_w', 'ctrl_x', 'ctrl_y', 'ctrl_z'])

combo_keys = ComboKeys('\x01', '\x02', '\x03', '\x04', '\x05',
                       '\x06', '\x07', '\x08', '\x09', '\x0a',
                       '\x0b', '\x0c', '\x0d', '\x0e', '\x0f',
                       '\x10', '\x11', '\x12', '\x13', '\x14',
                       '\x15', '\x16', '\x17', '\x18', '\x19', '\x1a')


class ActionRecorder:
    def __init__(self):
        self.recording = False
        self.playing = False
        self.events = []
        self.keyboard_listener = KeyboardListener(
            on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener = MouseListener(
            on_move=self.on_move, on_click=self.on_click)
        self.keyboard_controller = KeyboardController()
        self.mouse_controller = MouseController()
        self.last_event_time = None
        self.root = tk.Tk()
        self.root.withdraw()
        self.command_queue = Queue()

    def on_press(self, key):
        try:
            if hasattr(key, 'char'):
                if key.char == combo_keys.ctrl_r:  # Ctrl+R
                    if not self.recording and not self.playing:
                        self.recording = True
                        self.events = []
                        self.last_event_time = time.time()
                        print("Start recording...")
                        return
                    elif self.recording:
                        if self.events and (self.events[-1]['key'] == Key.ctrl_l or self.events[-1]['key'] == Key.ctrl_r):
                            self.events.pop()
                        self.recording = False
                        print("Recording ended...")
                        return
                if key.char == combo_keys.ctel_p:  # Ctrl+P
                    if not self.playing:
                        self.playing = True
                        print("Start playback...")
                        threading.Thread(target=self.play_events).start()
                        return
                    elif self.playing:
                        self.playing = False
                        print("Playback stopped...")
                        return
                if key.char == combo_keys.ctrl_s:  # Ctrl+S
                    self.command_queue.put(('save', None))
                    return
                if key.char == combo_keys.ctrl_l:  # Ctrl+L
                    self.command_queue.put(('load', None))
                    return
                if key.char == combo_keys.ctrl_q:  # Ctrl+Q
                    self.command_queue.put(('exit', None))
                    return

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
        except AttributeError:
            pass

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
            print(
                f"Recorded mouse click: {'Pressed' if pressed else 'Released'} at ({x}, {y})")

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
                    print(
                        f"Playing mouse click: {'Pressed' if pressed else 'Released'} at ({x}, {y})")
                    self.mouse_controller.position = (x, y)
                    if pressed:
                        self.mouse_controller.press(button)
                    else:
                        self.mouse_controller.release(button)
            time.sleep(1)

    def handle_commands(self):
        try:
            while True:
                command, _ = self.command_queue.get_nowait()
                if command == 'save':
                    self.save_events()
                elif command == 'load':
                    self.load_events()
                elif command == 'exit':
                    self.exit_app()
        except Empty:
            pass

    def serialize_event(self, event):
        """Serialize event so it can be stored as JSON."""
        event_copy = event.copy()
        if 'key' in event_copy:
            event_copy['key'] = self.serialize_key(event_copy['key'])
        if 'button' in event_copy:
            event_copy['button'] = self.serialize_button(event_copy['button'])
        return event_copy

    def serialize_key(self, key):
        """Serialize keyboard key to string."""
        if hasattr(key, 'char'):
            return f"KeyCode(char={repr(key.char)})"
        elif isinstance(key, keyboard.Key):
            return f"Key.{key.name}"
        return str(key)

    def serialize_button(self, button):
        """Serialize mouse button to string."""
        if isinstance(button, Button):
            return f"Button.{button.name}"
        return str(button)

    def save_events(self):
        filename = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON files', '*.json')],
            title="Save events as..."
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([self.serialize_event(e) for e in self.events], f)
            print(f"Events have been saved to {filename}")

    def load_events(self):
        filename = filedialog.askopenfilename(
            filetypes=[('JSON files', '*.json')],
            title="Load events from..."
        )
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                raw_events = json.load(f)
            self.events = [self.deserialize_event(e) for e in raw_events]
            print(f"Events have been loaded from {filename}")

    def deserialize_event(self, event):
        if 'key' in event:
            event['key'] = self.deserialize_key(event['key'])
        if 'button' in event:
            event['button'] = self.deserialize_button(event['button'])
        return event

    def deserialize_key(self, key_str):
        if key_str.startswith('KeyCode(char='):
            char_repr = key_str[len("KeyCode(char="):-1]
            char = char_repr.strip("'")
            return KeyCode(char=char)
        elif key_str.startswith('Key.'):
            key_name = key_str.split('.')[1]
            return getattr(Key, key_name)
        return key_str

    def deserialize_button(self, button_str):
        if button_str.startswith('Button.'):
            return getattr(Button, button_str.split('.')[1])
        return button_str

    def exit_app(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.root.quit()
        sys.exit(0)

    def run(self):
        threading.Thread(target=self.keyboard_listener.start).start()
        threading.Thread(target=self.mouse_listener.start).start()
        try:
            while True:
                self.root.update()
                self.handle_commands()
                time.sleep(0.1)
        except tk.TclError:
            pass  # Handle the exception if the window is closed


if __name__ == '__main__':
    recorder = ActionRecorder()
    recorder.run()
