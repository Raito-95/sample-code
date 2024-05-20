import os
from time import sleep, strftime, localtime
import requests
import pyautogui
from dotenv import load_dotenv

# Get the current directory of the script
current_directory = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

# Configuration
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")
SCREENSHOT_PATH = os.path.join(current_directory, "screenshots")
NOTIFICATION_MESSAGE = "New message here"
SLEEP_INTERVAL_SECONDS = 3600

# Ensure the 'screenshots' directory exists
os.makedirs(SCREENSHOT_PATH, exist_ok=True)


def take_screenshot(image_path):
    screenshot = pyautogui.screenshot()
    screenshot.save(image_path)


def send_line_notify(image_path):
    if LINE_NOTIFY_TOKEN is not None:
        headers = {"Authorization": "Bearer " + str(LINE_NOTIFY_TOKEN)}
        params = {"message": NOTIFICATION_MESSAGE}
        files = {"imageFile": open(image_path, "rb")}
        response = requests.post(
            "https://notify-api.line.me/api/notify",
            headers=headers,
            params=params,
            files=files,
            timeout=10,
        )
        return response.status_code
    else:
        print("LINE_NOTIFY_TOKEN is not set. Cannot send notification.")


if __name__ == "__main__":
    while True:
        current_time = strftime("%Y-%m-%d-%H", localtime())

        image_save = os.path.join(SCREENSHOT_PATH, current_time + ".png")

        take_screenshot(image_save)
        send_line_notify(image_save)

        print("Notification sent successfully")
        sleep(SLEEP_INTERVAL_SECONDS)
