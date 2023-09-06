import pyautogui
import keyboard


def start_loop():
    while True:      
        pyautogui.click(x=None, y=None, clicks=5, interval=0, button='left')

        if keyboard.is_pressed('x'):
            break

keyboard.add_hotkey('z', start_loop)
keyboard.wait()
