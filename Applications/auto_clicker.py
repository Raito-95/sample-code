import pyautogui
import keyboard

# Define a function to simulate mouse clicking
def start_loop():
    while True:
        # Simulate left mouse button click 5 times with no interval
        pyautogui.click(clicks=5, interval=0, button='left')

        # If the 'x' key is pressed, exit the loop and end the operation
        if keyboard.is_pressed('x'):
            break

# Set the hotkey 'z' to trigger the start_loop function when pressed
keyboard.add_hotkey('z', start_loop)

# Wait for a keyboard event, the program will run until the 'z' key is pressed
keyboard.wait()
