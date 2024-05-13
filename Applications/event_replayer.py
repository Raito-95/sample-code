import sys
import json
import time
import threading
from queue import Queue, Empty
from tkinter import filedialog
import tkinter as tk

from pynput import keyboard
from pynput.keyboard import Listener as KeyboardListener, Controller as KeyboardController, Key, KeyCode
from pynput.mouse import Listener as MouseListener, Controller as MouseController, Button


class ActionRecorder:
    function_keys = {
        Key.alt: "Alt", Key.alt_l: "Left Alt", Key.alt_r: "Right Alt",
        Key.alt_gr: "AltGr", Key.backspace: "Backspace", Key.caps_lock: "Caps Lock",
        Key.cmd: "Command", Key.cmd_l: "Left Command", Key.cmd_r: "Right Command",
        Key.ctrl: "Control", Key.ctrl_l: "Left Control", Key.ctrl_r: "Right Control",
        Key.delete: "Delete", Key.down: "Arrow Down", Key.end: "End",
        Key.enter: "Enter", Key.esc: "Escape",
        Key.f1: "F1", Key.f2: "F2", Key.f3: "F3", Key.f4: "F4",
        Key.f5: "F5", Key.f6: "F6", Key.f7: "F7", Key.f8: "F8",
        Key.f9: "F9", Key.f10: "F10", Key.f11: "F11", Key.f12: "F12",
        Key.home: "Home", Key.left: "Arrow Left", Key.page_down: "Page Down",
        Key.page_up: "Page Up", Key.right: "Arrow Right", Key.shift: "Shift",
        Key.shift_l: "Left Shift", Key.shift_r: "Right Shift", Key.space: "Space",
        Key.tab: "Tab", Key.up: "Arrow Up",
        Key.media_play_pause: "Media Play Pause", Key.media_volume_mute: "Media Volume Mute",
        Key.media_volume_down: "Volume Down", Key.media_volume_up: "Volume Up",
        Key.media_previous: "Previous Track", Key.media_next: "Next Track",
        Key.insert: "Insert", Key.menu: "Menu", Key.num_lock: "Num Lock",
        Key.pause: "Pause", Key.print_screen: "Print Screen", Key.scroll_lock: "Scroll Lock"
    }

    def __init__(self):
        self.recording = False
        self.playing = False
        self.events = []
        self.last_event_time = None
        self.command_queue = Queue()
        self.root = tk.Tk()
        self.root.withdraw()
        self.setup_listeners()
        print("[Info] ActionRecorder initialized and ready.")

    def setup_listeners(self):
        self.keyboard_listener = KeyboardListener(on_press=self.on_press)
        self.mouse_listener = MouseListener(on_move=self.on_move, on_click=self.on_click)
        self.keyboard_controller = KeyboardController()
        self.mouse_controller = MouseController()

    def on_press(self, key):
        try:
            if key == Key.delete:
                if not self.recording and not self.playing:
                    self.start_recording()
                elif self.recording:
                    self.stop_recording()
                return
            if key == Key.end:
                if not self.recording and not self.playing:
                    self.start_playback()
                elif self.playing:
                    self.stop_playback()
                return

            if key == Key.insert:
                self.command_queue.put(('Save', None))
                return
            if key == Key.home:
                self.command_queue.put(('Load', None))
                return
            if key == Key.page_down:
                self.command_queue.put(('Exit', None))
                return

            if key in self.function_keys:
                action = self.function_keys[key]
                if self.recording:
                    self.record_event({
                        'type': 'key',
                        'key': action
                    })
                return

            if self.recording:
                key_name = getattr(key, 'char', str(key))
                self.record_event({
                    'type': 'key',
                    'key': key_name,
                })

        except AttributeError:
            pass

    def start_recording(self):
        self.recording = True
        self.events = []
        self.last_event_time = time.time()
        print("[Info] Recording started.")

    def stop_recording(self):
        self.recording = False
        print("[Info] Recording stopped.")

    def start_playback(self):
        self.playing = True
        print("[Info] Playback started.")
        threading.Thread(target=self.play_events).start()

    def stop_playback(self):
        self.playing = False
        print("[Info] Playback stopped.")

    def record_event(self, event_info):
        if self.recording:
            now = time.perf_counter()
            delay = 0 if self.last_event_time is None else now - self.last_event_time
            event_info['delay'] = delay
            self.events.append(event_info)
            self.last_event_time = now
            event_type = event_info['type']
            print(f"[Event Recorded] Type: {event_type}, Info: {event_info}")

    def handle_control_command(self, command):
        self.command_queue.put((command, None))

    def on_release(self, key):
        pass

    def on_move(self, x, y):
        self.record_event({
            'type': 'move',
            'x': x,
            'y': y,
        })

    def on_click(self, x, y, button, pressed):
        self.record_event({
            'type': 'click',
            'x': x,
            'y': y,
            'button': button,
            'pressed': pressed,
        })

    def play_events(self):
        while self.playing:
            for event in self.events:
                if not self.playing:
                    break

                delay = max(event['delay'], 0)
                time.sleep(delay)

                self.process_event(event)

    def process_event(self, event):
        if 'type' not in event:
            print("[Error] Event type is missing from the event data.")
            return

        event_type = event['type']
        print(f"[Processing] Event type: {event_type}")

        if event_type == 'key':
            if 'key' not in event:
                return

            key_name = event['key']
            key = None

            if isinstance(key_name, Key):
                key = key_name
            else:
                for k, v in self.function_keys.items():
                    if v == key_name:
                        key = k
                        break

                if not key and isinstance(key_name, str) and len(key_name) == 1:
                    key = KeyCode(char=key_name)

            if key:
                self.keyboard_controller.press(key)
                self.keyboard_controller.release(key)
            else:
                print(f"[Error] Failed to resolve key from name: {key_name}")

        elif event_type == 'move':
            if 'x' not in event or 'y' not in event:
                return
            x = event['x']
            y = event['y']
            self.mouse_controller.position = (x, y)

        elif event_type == 'click':
            if 'button' not in event or 'pressed' not in event:
                return
            button = event['button']
            pressed = event['pressed']
            action = self.mouse_controller.press if pressed else self.mouse_controller.release
            action(button)

    def handle_commands(self):
        try:
            while True:
                command, _ = self.command_queue.get_nowait()
                if command == 'Save':
                    self.save_events()
                elif command == 'Load':
                    self.load_events()
                elif command == 'Exit':
                    self.exit_app()
        except Empty:
            pass

    def serialize_event(self, event):
        event_copy = event.copy()
        if 'key' in event_copy:
            event_copy['key'] = self.serialize_key(event_copy['key'])
        if 'button' in event_copy:
            event_copy['button'] = self.serialize_button(event_copy['button'])
        return event_copy

    def serialize_key(self, key):
        if hasattr(key, 'char'):
            return f"KeyCode(char={repr(key.char)})"
        elif isinstance(key, keyboard.Key):
            return f"Key.{key.name}"
        return str(key)

    def serialize_button(self, button):
        if isinstance(button, Button):
            return f"Button.{button.name}"
        return str(button)

    def save_events(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension='.json',
                filetypes=[('JSON files', '*.json')],
                title="Save events as..."
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump([self.serialize_event(e) for e in self.events], f)
        except Exception as e:
            print(f"[Error] Failed to save events: {str(e)}")


    def deserialize_event(self, event):
        if 'key' in event:
            event['key'] = self.deserialize_key(event['key'])
        if 'button' in event:
            event['button'] = self.deserialize_button(event['button'])
        return event

    def deserialize_key(self, key_str):
        if key_str in self.function_keys.values():
            for key, value in self.function_keys.items():
                if value == key_str:
                    return key
        elif key_str.startswith('KeyCode(char='):
            return KeyCode(char=key_str[len("KeyCode(char="):-1].strip("'"))
        elif key_str.startswith('Key.'):
            return getattr(Key, key_str.split('.')[1])
        return key_str

    def deserialize_button(self, button_str):
        if button_str.startswith('Button.'):
            return getattr(Button, button_str.split('.')[1])
        return button_str

    def load_events(self):
        filename = filedialog.askopenfilename(
            filetypes=[('JSON files', '*.json')],
            title="Load events from..."
        )
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                raw_events = json.load(f)
            self.events = [self.deserialize_event(e) for e in raw_events]

    def exit_app(self):
        try:
            self.keyboard_listener.stop()
            self.mouse_listener.stop()
            self.root.quit()
            sys.exit(0)
        except Exception as e:
            print(f"[Error] Failed to exit application cleanly: {str(e)}")

    def run(self):
        threading.Thread(target=self.keyboard_listener.start).start()
        threading.Thread(target=self.mouse_listener.start).start()
        try:
            while True:
                self.root.update()
                self.handle_commands()
                time.sleep(0.1)
        except tk.TclError:
            pass


if __name__ == '__main__':
    recorder = ActionRecorder()
    recorder.run()
