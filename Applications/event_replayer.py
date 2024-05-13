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
                self.toggle_recording()
            elif key == Key.end:
                self.toggle_playback()
            elif key == Key.insert:
                self.command_queue.put(('Save', None))
            elif key == Key.home:
                self.command_queue.put(('Load', None))
            elif key == Key.page_down:
                self.command_queue.put(('Exit', None))
            elif self.recording:
                if isinstance(key, keyboard.Key):
                    self.record_event({
                        'type': 'key',
                        'key': key.name
                    })
                else:
                    key_name = getattr(key, 'char', str(key))
                    self.record_event({
                        'type': 'key',
                        'key': key_name,
                    })
        except AttributeError:
            pass

    def toggle_recording(self):
        if not self.recording and not self.playing:
            self.start_recording()
        elif self.recording:
            self.stop_recording()

    def start_recording(self):
        self.recording = True
        self.events = []
        self.last_event_time = time.time()
        print("[Info] Recording started.")

    def stop_recording(self):
        self.recording = False
        print("[Info] Recording stopped.")

    def toggle_playback(self):
        if not self.recording and not self.playing:
            self.start_playback()
        elif self.playing:
            self.stop_playback()

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

        if event_type == 'key':
            key = event['key']
            print(f"[Processing] Event type: key, key: {key}")
            if isinstance(key, str) and hasattr(Key, key):
                key = getattr(Key, key)

            if key:
                self.keyboard_controller.press(key)
                self.keyboard_controller.release(key)
            else:
                print(f"[Error] Failed to resolve key from name: {key}")

        elif event_type == 'move':
            if 'x' not in event or 'y' not in event:
                print("[Error] Missing coordinates for mouse movement.")
                return
            x, y = event['x'], event['y']
            self.mouse_controller.position = (x, y)

        elif event_type == 'click':
            button = event['button']
            print(f"[Processing] Event type: click, button: {button}")
            if button:
                action = self.mouse_controller.press if event['pressed'] else self.mouse_controller.release
                action(button)
            else:
                print(f"[Error] Failed to resolve button from name: {button}")

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
        for attr in ['key', 'button']:
            if attr in event_copy:
                event_copy[attr] = self.serialize_attribute(event_copy[attr])
        return event_copy

    def serialize_attribute(self, attribute):
        if isinstance(attribute, KeyCode) and hasattr(attribute, 'char'):
            return f"KeyCode(char={repr(attribute.char)})"
        elif isinstance(attribute, Key):
            return f"Key.{attribute.name}"
        elif isinstance(attribute, Button):
            return f"Button.{attribute.name}"
        return str(attribute)

    def deserialize_event(self, event):
        for attr in ['key', 'button']:
            if attr in event:
                event[attr] = self.deserialize_attribute(event[attr], attr)
        return event

    def deserialize_attribute(self, attribute_str, attr_type):
        module = Key if attr_type == 'key' else Button
        if attribute_str.startswith(f'{attr_type.title()}.'):
            item_name = attribute_str.split('.')[1]
            return getattr(module, item_name)
        elif attr_type == 'key' and attribute_str.startswith('KeyCode(char='):
            char = attribute_str[len("KeyCode(char="):-1].strip("'")
            return KeyCode(char=char)
        return attribute_str

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

    def load_events(self):
        try:
            filename = filedialog.askopenfilename(
                filetypes=[('JSON files', '*.json')],
                title="Load events from..."
            )
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    raw_events = json.load(f)
                self.events = [self.deserialize_event(e) for e in raw_events]
        except Exception as e:
            print(f"[Error] Failed to load events: {str(e)}")

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
