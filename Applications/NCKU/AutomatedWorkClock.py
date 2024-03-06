import os
import json
import time
import random
import logging
from datetime import datetime, timedelta
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import holidays

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the path to the JSON file containing configuration settings
json_file_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
# Initialize holidays for Taiwan
tw_holidays = holidays.Taiwan()

def validate_config(config):
    """Validate the configuration settings."""
    required_keys = ['psn_code', 'password', 'line_notify_token', 'sign_in_minute_start', 'sign_in_minute_end']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing '{key}' in configuration.")

    if not (0 <= config['sign_in_minute_start'] < config['sign_in_minute_end'] <= 60):
        raise ValueError("Invalid sign-in minute range in configuration.")

def is_holiday(date):
    """Check if the given date is a holiday in Taiwan."""
    return date in tw_holidays

def setup_driver():
    """Set up the Chrome WebDriver with headless mode and disabled GPU acceleration."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def login(driver, psn_code, password):
    """Log into the website using the provided credentials."""
    driver.get("https://eadm.ncku.edu.tw/welldoc/ncku/iftwd/signIn.php")
    driver.find_element(By.ID, "psnCode").send_keys(psn_code)
    driver.find_element(By.ID, "password").send_keys(password)

    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
    except TimeoutException:
        pass

def click_button(driver, button_text, wait_time=10):
    """Wait for a button with the specified text to be clickable and then click it."""
    wait = WebDriverWait(driver, wait_time)
    button_xpath = f"//button[contains(text(), '{button_text}')]"
    button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
    button.click()
    time.sleep(5)

def view_swipe_card_records(driver, wait_time=10):
    """Clicks the button to view today's swipe card records and extracts the data."""
    click_button(driver, "查看本日刷卡紀錄", wait_time=wait_time)

    wait = WebDriverWait(driver, wait_time)
    table_xpath = "//table[@id='checkinList']"
    table = wait.until(EC.visibility_of_element_located((By.XPATH, table_xpath)))
    rows = table.find_elements(By.TAG_NAME, "tr")
    records = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            record = {
                "date": cols[0].text,
                "weekDay": cols[1].text,
                "className": cols[2].text,
                "time": cols[3].text,
                "ip": cols[4].text
            }
            records.append(record)
    return records

def send_line_notify(token, message):
    """Sends a notification message via LINE Notify."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"message": message}
    response = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data, timeout=10)
    if response.status_code != 200:
        logging.error("Failed to send LINE Notify message: %s", response.text)
    return response.status_code == 200

def format_records(records, sign_type):
    """Formats a list of swipe card records into a string for display or messaging."""
    if sign_type not in ['sign_in', 'sign_out']:
        return "Invalid sign type."
    if not records:
        return "No records found."
    record = records[0] if sign_type == 'sign_in' else records[-1]
    return f"Date: {record['date']}\nWeekDay: {record['weekDay']}\nClass: {record['className']}\nTime: {record['time']}\nIP: {record['ip']}\n"

def perform_sign_in_out(driver, config, sign_type):
    """Performs the sign-in or sign-out operation and sends a notification."""
    button_text = "上班簽到" if sign_type == "sign_in" else "下班簽退"
    click_button(driver, button_text)
    records = view_swipe_card_records(driver)
    expected_records = 1 if sign_type == "sign_in" else 2
    if len(records) != expected_records:
        click_button(driver, button_text)
        records = view_swipe_card_records(driver)
        if len(records) != expected_records:
            send_line_notify(config['line_notify_token'], f"\n{button_text}失敗!\n請手動確認。")
            return
    records_str = format_records(records, sign_type)
    send_line_notify(config['line_notify_token'], f"\n{button_text}成功!\n{records_str}")

def handle_sign_in_out(config):
    """Handles the sign-in and sign-out process based on the current time and workday schedule."""
    current_time = datetime.now()
    sign_in_hour = 8

    # Calculate sign-in and sign-out times for today
    today_sign_in_time = datetime(current_time.year, current_time.month, current_time.day, sign_in_hour, config['sign_in_minute_start'])
    today_sign_out_time = today_sign_in_time + timedelta(hours=9, minutes=5)

    # If the current time is before today's sign-in time, wait until sign-in time
    if current_time < today_sign_in_time:
        while datetime.now() < today_sign_in_time:
            time.sleep(60)
        driver = setup_driver()
        login(driver, config['psn_code'], config['password'])
        perform_sign_in_out(driver, config, "sign_in")
        driver.quit()

        # Wait until sign-out time
        while datetime.now() < today_sign_out_time:
            time.sleep(60)
        driver = setup_driver()
        login(driver, config['psn_code'], config['password'])
        perform_sign_in_out(driver, config, "sign_out")
        driver.quit()

    # If the current time is during work hours, prompt for sign-in time and wait until sign-out
    elif today_sign_in_time <= current_time < today_sign_out_time:
        while True:
            sign_in_minute_input = input("請輸入上班時間的分鐘數(格式:MM): ")
            try:
                sign_in_minute = int(sign_in_minute_input)
                if config['sign_in_minute_start'] <= sign_in_minute < config['sign_in_minute_end']:
                    print("已輸入有效的上班時間，程式現在將進入等待狀態，直到簽退時間。")
                    break
                else:
                    print(f"請輸入{config['sign_in_minute_start']}到{config['sign_in_minute_end'] - 1}之間的分鐘數")
            except ValueError:
                print("分鐘數格式不正確，請重新輸入。")

        sign_in_datetime = current_time.replace(minute=sign_in_minute, second=0, microsecond=0)
        sign_out_time = sign_in_datetime + timedelta(hours=9, minutes=5)

        while datetime.now() < sign_out_time:
            time.sleep(60)
        driver = setup_driver()
        login(driver, config['psn_code'], config['password'])
        perform_sign_in_out(driver, config, "sign_out")
        driver.quit()

    # Handle automatic sign-in and sign-out for future days
    while True:
        next_workday = current_time + timedelta(days=1)
        while next_workday.weekday() in [5, 6] or is_holiday(next_workday.date()):
            next_workday += timedelta(days=1)
        sign_in_time = next_workday.replace(hour=sign_in_hour, minute=random.randint(config['sign_in_minute_start'], config['sign_in_minute_end'] - 1), second=0, microsecond=0)
        sign_out_time = sign_in_time + timedelta(hours=9, minutes=5)

        while datetime.now() < sign_in_time:
            time.sleep(60)
        driver = setup_driver()
        login(driver, config['psn_code'], config['password'])
        perform_sign_in_out(driver, config, "sign_in")
        driver.quit()

        while datetime.now() < sign_out_time:
            time.sleep(60)
        driver = setup_driver()
        login(driver, config['psn_code'], config['password'])
        perform_sign_in_out(driver, config, "sign_out")
        driver.quit()
        current_time = datetime.now()

def main():
    """Main function to read configuration and start the sign-in and sign-out process."""
    try:
        with open(json_file_path, 'r', encoding="utf-8") as file:
            config = json.load(file)
        validate_config(config)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        logging.error("Error reading or validating configuration: %s", e)
        return

    handle_sign_in_out(config)

if __name__ == "__main__":
    main()
