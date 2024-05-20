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
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(image_path)
        print(f"Screenshot saved to {image_path}")
    except Exception as e:
        print(f"Failed to take screenshot: {e}")


def send_line_notify(image_path):
    if LINE_NOTIFY_TOKEN is not None:
        headers = {"Authorization": "Bearer " + str(LINE_NOTIFY_TOKEN)}
        params = {"message": NOTIFICATION_MESSAGE}
        try:
            with open(image_path, "rb") as image_file:
                files = {"imageFile": image_file}
                response = requests.post(
                    "https://notify-api.line.me/api/notify",
                    headers=headers,
                    params=params,
                    files=files,
                    timeout=10,
                )
            if response.status_code == 200:
                print("Notification sent successfully")
            else:
                print(
                    f"Failed to send notification: {response.status_code} - {response.text}"
                )
        except Exception as e:
            print(f"Error sending notification: {e}")
    else:
        print("LINE_NOTIFY_TOKEN is not set. Cannot send notification.")


if __name__ == "__main__":
    while True:
        current_time = strftime("%Y-%m-%d-%H", localtime())
        image_save = os.path.join(SCREENSHOT_PATH, current_time + ".png")

        take_screenshot(image_save)
        send_line_notify(image_save)

        sleep(SLEEP_INTERVAL_SECONDS)
