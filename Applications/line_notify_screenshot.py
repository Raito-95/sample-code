from time import sleep, strftime, localtime
import pyautogui
import requests

# Configuration
SCREENSHOT_PATH = ''
SLEEP_INTERVAL_SECONDS = 3600  # 1 hour
LINE_NOTIFY_TOKEN = ''  # Fill in your LINE Notify Token
NOTIFICATION_MESSAGE = 'Success'

def take_screenshot(image_path):
    screenshot = pyautogui.screenshot()
    screenshot.save(image_path)

def send_line_notify(image_path):
    headers = {"Authorization": "Bearer " + LINE_NOTIFY_TOKEN}
    params = {'message': NOTIFICATION_MESSAGE}
    files = {'imageFile': open(image_path, 'rb')}
    response = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=params, files=files)
    return response.status_code

if __name__ == '__main__':
    while True:
        current_time = strftime("%Y-%m-%d-%H", localtime())
        image_save = SCREENSHOT_PATH + current_time + '.png'
        
        take_screenshot(image_save)
        send_line_notify(image_save)
        
        print('Notification sent successfully')
        sleep(SLEEP_INTERVAL_SECONDS)
