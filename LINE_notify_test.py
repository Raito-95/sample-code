from time import sleep
import time
import requests
import pyautogui


current_time = time.strftime("%Y-%m-%d-%H", time.localtime(time.time()))
screen_image_path = 'D:/GitHub/python-code/image/' + current_time + '.png'


def screenshot(image):
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(image)
    return image


def lineNotifyMessage(image):
    token = ''

    headers = {"Authorization": "Bearer " + token}
    params = {'message': 'success'}
    files = {'imageFile': open(image, 'rb')}

    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=params, files=files)
    return r.status_code


if __name__ == '__main__':

    while True:

        image_save = screenshot(screen_image_path)
        lineNotifyMessage(image_save)
        print('end')

        sleep(3600)






