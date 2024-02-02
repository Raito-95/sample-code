import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_line_notify(notification_message):
    line_notify_token = os.getenv('LINE_NOTIFY_TOKEN')
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': f'message: {notification_message}'}
    requests.post(line_notify_api, headers=headers, data=data)

def check_website(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            send_line_notify(f"Website {url} is up and running. Status code: 200")
        else:
            send_line_notify(f"Website {url} returned status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        send_line_notify(f"Website {url} is down. Error: {e}")

url_to_check = os.getenv('URL_TO_CHECK')
check_website(url_to_check)
