import sys
import json
import time
import threading
import tkinter as tk
from tkinter import filedialog

from pynput.keyboard import (
    Listener as KeyboardListener,
    Controller as KeyboardController,
    Key,
    KeyCode,
)
from pynput.mouse import (
    Listener as MouseListener,
    Controller as MouseController,
    Button,
)


class ActionRecorder:
    def __init__(self):
        self.recording = False
        self.playing = False
        self.events = []
        self.last_event_time = None
        self.root = tk.Tk()
        self.root.withdraw()
        self.setup_listeners()

    def setup_listeners(self):
        self.keyboard_listener = KeyboardListener(on_press=self.on_press)
        self.mouse_listener = MouseListener(
            on_move=self.on_move, on_click=self.on_click
        )
        self.keyboard_controller = KeyboardController()
        self.mouse_controller = MouseController()

    def on_press(self, key):
        if key == Key.delete:
            self.toggle_recording()
        elif key == Key.end:
            self.toggle_playback()
        elif key == Key.insert:
            self.save_events()
        elif key == Key.home:
            self.load_events()
        elif key == Key.page_down:
            self.exit_app()
        elif self.recording:
            self.record_event({"type": "key", "key": self.serialize_key(key)})

    def serialize_key(self, key):
        if isinstance(key, Key):
            return f"Key.{key.name}"
        elif isinstance(key, KeyCode):
            return f"KeyCode(char={repr(key.char)})"
        return None

    def deserialize_key(self, key_str):
        if "Key." in key_str:
            key_name = key_str.split(".")[-1]
            try:
                return getattr(Key, key_name)
            except AttributeError:
                print(f"[Error] Key attribute '{key_name}' not found in Key")
                return None
        elif "KeyCode(char=" in key_str:
            try:
                char = key_str.split("=")[-1].rstrip(")")
                return KeyCode(char=char.strip("'"))
            except ValueError:
                print(f"[Error] Invalid KeyCode value in {key_str}")
                return None
        else:
            print(f"[Error] Unable to deserialize key '{key_str}'")
            return None

    def toggle_recording(self):
        if self.playing:
            print("[Warning] Cannot start recording while playback is active.")
            return
        self.recording = not self.recording
        if self.recording:
            self.events = []
            self.last_event_time = None
        print(
            f"[Info] Recording toggled. State: {'Recording' if self.recording else 'Not recording'}"
        )

    def toggle_playback(self):
        if self.recording:
            print("[Warning] Cannot start playback while recording is active.")
            return
        if not self.playing:
            self.playing = True
            threading.Thread(target=self.play_events, daemon=True).start()
        else:
            self.playing = False
        print(
            f"[Info] Playback toggled. State: {'Playing' if self.playing else 'Not playing'}"
        )

    def record_event(self, event_info):
        if self.recording:
            now = time.time()
            event_info["delay"] = (
                0 if self.last_event_time is None else now - self.last_event_time
            )
            self.events.append(event_info)
            self.last_event_time = now
            print(f"[Info] Recorded event: {event_info}")

    def on_move(self, x, y):
        if self.recording:
            self.record_event({"type": "move", "x": x, "y": y})

    def on_click(self, x, y, button, pressed):
        if self.recording:
            self.record_event(
                {
                    "type": "click",
                    "x": x,
                    "y": y,
                    "button": button.name,
                    "pressed": pressed,
                }
            )

    def play_events(self):
        while self.playing:
            for event in self.events:
                if not self.playing:
                    break
                time.sleep(max(event.get("delay", 0), 0))
                self.process_event(event)
                print(f"[Info] Executed event: {event}")
            print("[Info] Playback finished. Restarting...")

    def process_event(self, event):
        event_type = event.get("type")
        if event_type == "key":
            key = self.deserialize_key(event["key"])
            if isinstance(key, (Key, KeyCode)):
                self.keyboard_controller.press(key)
                self.keyboard_controller.release(key)
            else:
                print(f"[Error] Invalid or unresolved key object: {event['key']}")
        elif event_type == "move":
            self.mouse_controller.position = (event["x"], event["y"])
        elif event_type == "click":
            button = Button[event["button"]]
            action = (
                self.mouse_controller.press
                if event["pressed"]
                else self.mouse_controller.release
            )
            action(button)

    def save_events(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save events as...",
        )
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.events, f)
            print(f"[Info] Events saved to {filename}")

    def load_events(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")], title="Load events from..."
        )
        if filename:
            with open(filename, "r", encoding="utf-8") as f:
                self.events = json.load(f)
            print(f"[Info] Events loaded from {filename}")

    def exit_app(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.playing = False
        print("[Info] Exiting application.")
        self.root.quit()
        self.root.update()
        sys.exit(0)

    def run(self):
        threading.Thread(target=self.keyboard_listener.start).start()
        threading.Thread(target=self.mouse_listener.start).start()
        self.root.mainloop()


if __name__ == "__main__":
    recorder = ActionRecorder()
    recorder.run()
