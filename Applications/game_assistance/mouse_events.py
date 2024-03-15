import tkinter as tk
import pyautogui
import time
import json
import threading
import keyboard
from pynput.mouse import Listener as MouseListener

class MouseRecorder:
    def __init__(self):
        """
        Initializes the MouseRecorder with the required attributes and starts the mouse listener.
        """
        self.events = []
        self.recording = False
        self.playing = False
        self.paused = False
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.label = tk.Label(self.root, text="Press F1 to start/pause recording, F2 to stop, F3 to play/pause")
        self.label.pack()

        self.loop_playback_var = tk.BooleanVar()
        self.loop_playback_check = tk.Checkbutton(self.root, text="Loop playback", variable=self.loop_playback_var)
        self.loop_playback_check.pack()

        keyboard.add_hotkey('F1', self.toggle_recording_or_pause)
        keyboard.add_hotkey('F2', self.stop_recording)
        keyboard.add_hotkey('F3', self.toggle_playback)

        self.mouse_listener = MouseListener(on_click=self.on_click)
        self.mouse_listener.start()

    def on_click(self, x, y, button, pressed):
        """
        Callback function for mouse click events.

        :param x: X coordinate of the mouse click.
        :param y: Y coordinate of the mouse click.
        :param button: The button that was clicked.
        :param pressed: Boolean indicating whether the button was pressed or released.
        """
        if self.recording and not self.paused:
            event_type = 'Click' if pressed else 'Release'
            event = {'x': x, 'y': y, 'type': event_type, 'timestamp': time.time()}
            self.events.append(event)

    def toggle_recording_or_pause(self):
        """
        Toggles the recording state or pauses the recording.
        """
        if not self.recording:
            self.recording = True
            self.paused = False
            self.label.config(text="Recording...")
            self.events = []
            self.record_mouse_events()
        elif self.paused:
            self.paused = False
            self.label.config(text="Recording resumed")
            self.record_mouse_events()
        else:
            self.paused = True
            self.label.config(text="Recording paused")

    def record_mouse_events(self):
        """
        Records mouse movement events.
        """
        if self.recording and not self.paused:
            x, y = pyautogui.position()
            event = {'x': x, 'y': y, 'type': 'Move', 'timestamp': time.time()}
            self.events.append(event)
            self.root.after(100, self.record_mouse_events)

    def save_events_to_file(self, filename='mouse_events.json'):
        """
        Saves the recorded events to a JSON file.

        :param filename: The name of the file to save the events to.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.events, f)

    def load_events_from_file(self, filename='mouse_events.json'):
        """
        Loads the recorded events from a JSON file.

        :param filename: The name of the file to load the events from.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.events = json.load(f)
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
            self.events = []

    def stop_recording(self):
        """
        Stops the recording of mouse events and saves them to a file.
        """
        if self.recording:
            self.recording = False
            self.paused = False
            self.label.config(text="Recording stopped.")
            self.save_events_to_file()

    def toggle_playback(self):
        """
        Toggles the playback of the recorded mouse events.
        """
        if not self.playing:
            self.playing = True
            self.paused = False
            self.label.config(text="Playing...")
            threading.Thread(target=self.play_recorded_events).start()
        else:
            self.paused = not self.paused
            self.label.config(text="Playback paused." if self.paused else "Playing...")

    def play_recorded_events(self):
        """
        Plays back the recorded mouse events.
        """
        self.load_events_from_file()
        if not self.events:
            print("No events loaded.")
            return

        while self.playing:
            start_time = time.time()
            initial_timestamp = self.events[0]['timestamp'] if self.events else 0

            for event in self.events:
                if not self.playing or self.paused:
                    continue

                current_time = time.time()
                elapsed_event_time = event['timestamp'] - initial_timestamp
                target_time = start_time + elapsed_event_time

                if event['type'] == 'Move':
                    pyautogui.moveTo(event['x'], event['y'], duration=0.1)
                    time.sleep(max(0, 0.05 - (time.time() - current_time)))
                elif event['type'] in ['Click', 'Release']:
                    if event['type'] == 'Click':
                        pyautogui.mouseDown(x=event['x'], y=event['y'])
                    else:
                        pyautogui.mouseUp(x=event['x'], y=event['y'])

                while time.time() < target_time:
                    time.sleep(0.01)

            if not self.loop_playback_var.get():
                break

        self.playing = False
        self.label.config(text="Finished playing.")

    def start(self):
        """
        Starts the main loop of the Tkinter GUI.
        """
        self.root.mainloop()

# Main program
recorder = MouseRecorder()
recorder.start()
