# Import necessary modules
from time import sleep
import time
import requests
import pyautogui

# Get the current time for the file name
current_time = time.strftime("%Y-%m-%d-%H", time.localtime(time.time()))
screen_image_path = 'D:/GitHub/python-code/image/' + current_time + '.png'  # File path for the screen capture

# Function: Take a screenshot
def screenshot(image):
    my_screenshot = pyautogui.screenshot()  # Capture the screen using PyAutoGUI
    my_screenshot.save(image)  # Save the screenshot to the specified path
    return image

# Function: Send a notification using LINE Notify
def line_notify_message(image):
    token = ''  # Please fill in your LINE Notify Token here

    headers = {"Authorization": "Bearer " + token}
    params = {'message': 'Success'}  # Notification message
    files = {'imageFile': open(image, 'rb')}  # Image file to be sent

    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=params, files=files)  # Send the notification using a POST request
    return r.status_code  # Return the HTTP status code

if __name__ == '__main__':
    while True:
        image_save = screenshot(screen_image_path)  # Capture the screen and save it
        line_notify_message(image_save)  # Send a LINE notification
        print('Notification sent successfully')
        sleep(3600)  # Run the program every 3600 seconds (1 hour)
