import pyautogui
import time
import keyboard
import json

class MouseRecorder:
    def __init__(self):
        self.events = []
        self.recording = False
        self.paused = False

    def record_mouse_events(self):
        """
        Record mouse events.

        Returns:
            list: A list of dictionaries representing mouse events.
        """
        self.events = []
        self.recording = False
        self.paused = False

        while True:
            if keyboard.is_pressed('F1') and not self.recording:
                print("Recording started...")
                self.recording = True
            elif keyboard.is_pressed('F2'):
                self.paused = not self.paused
                if self.paused:
                    print("Recording paused...")
                else:
                    print("Recording resumed...")
                time.sleep(0.2)
            elif keyboard.is_pressed('F3'):
                if self.recording:
                    print("Recording stopped.")
                    break

            if self.recording and not self.paused:
                x, y = pyautogui.position()
                event_type = 'Move'
                if pyautogui.mouseDown():
                    event_type = 'Click'

                event = {'x': x, 'y': y, 'type': event_type, 'timestamp': time.time()}
                self.events.append(event)

            time.sleep(0.1)

        return self.events

    def save_events_to_file(self, filename='mouse_events.json'):
        """
        Save events to file.

        Args:
            filename (str): The name of the file to save events to. Default is 'mouse_events.json'.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.events, f)

    def load_events_from_file(self, filename='mouse_events.json'):
        """
        Load events from file.

        Args:
            filename (str): The name of the file to load events from. Default is 'mouse_events.json'.

        Returns:
            list: A list of dictionaries representing mouse events.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.events = json.load(f)
            return self.events
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
            return None

    def play_recorded_events(self):
        """
        Play recorded events.
        """
        if not self.events:
            print("No events loaded.")
            return

        start_time = self.events[0]['timestamp']
        for event in self.events:
            if event['type'] == 'Move':
                pyautogui.moveTo(event['x'], event['y'], duration=0.1)
            elif event['type'] == 'Click':
                pyautogui.click()

            elapsed_time = event['timestamp'] - start_time
            time.sleep(max(0, event['timestamp'] - time.time() - start_time))

# Main program
print("Press F1 to start recording, F2 to pause/resume, F3 to stop recording...")
recorder = MouseRecorder()
events = recorder.record_mouse_events()

if events:
    recorder.save_events_to_file()
    print("Recording saved to mouse_events.json.")

print("Press F4 to play recorded events...")
events = recorder.load_events_from_file()

if events:
    print("Press F5 to stop playing...")
    while not keyboard.is_pressed('F5'):
        if keyboard.is_pressed('F4'):
            print("Playing recorded events...")
            recorder.play_recorded_events()
