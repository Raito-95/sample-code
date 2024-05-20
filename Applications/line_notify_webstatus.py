import os
import requests
from dotenv import load_dotenv

load_dotenv()


def send_line_notify(notification_message):
    line_notify_token = os.getenv("LINE_NOTIFY_TOKEN")
    if not line_notify_token:
        print("LINE_NOTIFY_TOKEN is not set. Cannot send notification.")
        return

    line_notify_api = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {line_notify_token}"}
    data = {"message": f"message: {notification_message}"}

    try:
        response = requests.post(
            line_notify_api, headers=headers, data=data, timeout=10
        )
        if response.status_code == 200:
            print("Notification sent successfully")
        else:
            print(
                f"Failed to send notification: {response.status_code} - {response.text}"
            )
    except requests.exceptions.RequestException as e:
        print(f"Error sending notification: {e}")


def check_website(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            send_line_notify(f"Website {url} is up and running. Status code: 200")
        else:
            send_line_notify(
                f"Website {url} returned status code {response.status_code}"
            )
    except requests.exceptions.RequestException as e:
        send_line_notify(f"Website {url} is down. Error: {e}")


if __name__ == "__main__":
    url_to_check = os.getenv("URL_TO_CHECK")
    if not url_to_check:
        print("URL_TO_CHECK is not set. Cannot check website.")
    else:
        check_website(url_to_check)
