import os
import json
import time
import random
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

json_file_path = os.path.join(os.path.dirname(__file__), 'credentials.json')

def setup_driver():
    """
    Sets up the Chrome WebDriver with headless mode and disabled GPU acceleration.
    Uses webdriver-manager to automatically manage the ChromeDriver binary.
    Returns the configured WebDriver instance.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration

    # Set up the Chrome driver with the latest version using webdriver-manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def login(driver, psn_code, password):
    """
    Logs into the website using the provided credentials.
    Parameters:
        driver: The WebDriver instance.
        psn_code: The user's personal code.
        password: The user's password.
    """
    driver.get("https://eadm.ncku.edu.tw/welldoc/ncku/iftwd/signIn.php")
    driver.find_element(By.ID, "psnCode").send_keys(psn_code)
    driver.find_element(By.ID, "password").send_keys(password)

    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
    except TimeoutException:
        pass  # No alert present

def view_swipe_card_records(driver):
    """
    Clicks the button to view today's swipe card records and extracts the data from the displayed table.
    Parameters:
        driver: The WebDriver instance.
    Returns:
        A list of dictionaries, each representing a record with keys: date, weekDay, className, time, and ip.
    """
    wait = WebDriverWait(driver, 10)
    button_xpath = "//button[contains(text(), '查看本日刷卡紀錄')]"
    button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
    button.click()

    time.sleep(5)  # Wait for the table to be rendered

    table_xpath = "//table[@id='checkinList']"
    table = wait.until(EC.visibility_of_element_located((By.XPATH, table_xpath)))
    rows = table.find_elements(By.TAG_NAME, "tr")
    records = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:  # Skip the header row
            record = {
                "date": cols[0].text,
                "weekDay": cols[1].text,
                "className": cols[2].text,
                "time": cols[3].text,
                "ip": cols[4].text
            }
            records.append(record)
    
    return records

def click_button(driver, button_text):
    """
    Waits for a button with the specified text to be clickable and then clicks it.
    Parameters:
        driver: The WebDriver instance.
        button_text: The text of the button to be clicked.
    """
    wait = WebDriverWait(driver, 10)
    button_xpath = f"//button[contains(text(), '{button_text}')]"
    button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
    button.click()
    time.sleep(5)  # Wait for a moment to ensure the action is completed

def send_line_notify(token, message):
    """
    Sends a notification message via LINE Notify.
    Parameters:
        token: The LINE Notify access token.
        message: The message to be sent.
    Returns:
        True if the message was sent successfully, False otherwise.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"message": message}
    response = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data, timeout=10)
    return response.status_code == 200

def format_records(records, sign_type):
    """
    Formats a list of swipe card records into a string for display or messaging.
    Parameters:
        records: A list of dictionaries, each representing a swipe card record.
        sign_type: A string indicating the type of sign action ('sign_in' or 'sign_out').
    Returns:
        A formatted string representing the records.
    """
    if sign_type == 'sign_in':
        # For sign-in, use only the first record
        record = records[0]
        return f"Date: {record['date']}\nWeekDay: {record['weekDay']}\nClass: {record['className']}\nTime: {record['time']}\nIP: {record['ip']}\n"
    elif sign_type == 'sign_out':
        # For sign-out, use only the second record
        if len(records) > 1:
            record = records[1]
            return f"Date: {record['date']}\nWeekDay: {record['weekDay']}\nClass: {record['className']}\nTime: {record['time']}\nIP: {record['ip']}\n"
        else:
            return "No sign-out record found."
    else:
        return "Invalid sign type."

def handle_immediate_sign_out(config, current_time):
    """
    Handles the immediate sign-out process if the script is run during work hours.
    Prompts the user to input the sign-in time, waits until the sign-out time, and performs the sign-out operation.
    Parameters:
        config: A dictionary containing configuration settings such as credentials and LINE Notify token.
        current_time: A datetime object representing the current time.
    """
    # Prompt the user to input the sign-in time
    while True:
        sign_in_time_input = input("請輸入上班時間(格式:HH:MM):")
        sign_in_time = datetime.strptime(sign_in_time_input, "%H:%M").time()
        if datetime.strptime("08:00", "%H:%M").time() <= sign_in_time <= datetime.strptime("08:25", "%H:%M").time():
            print("已輸入有效的上班時間，程式現在將進入等待狀態，直到簽退時間。")
            break
        else:
            print("請輸入8:00到8:25之間的時間")

    # Calculate the sign-out time based on the user input
    sign_in_datetime = current_time.replace(hour=sign_in_time.hour, minute=sign_in_time.minute, second=0, microsecond=0)
    sign_out_time = (sign_in_datetime + timedelta(hours=9, minutes=5)).time()

    # Wait until sign-out time
    while current_time.time() < sign_out_time:
        time.sleep(60)  # Check every minute
        current_time = datetime.now()

    # Perform the sign-out operation
    driver = setup_driver()
    login(driver, config['psn_code'], config['password'])
    click_button(driver, "下班簽退")
    records = view_swipe_card_records(driver)
    if len(records) != 2:  # Retry if the number of records is not as expected
        click_button(driver, "下班簽退")
        records = view_swipe_card_records(driver)
        if len(records) != 2:  # Send failure message if still not as expected
            send_line_notify(config['line_notify_token'], "\n下班簽退失敗!\n請手動確認。")
        else:
            records_str = format_records(records, 'sign_out')
            send_line_notify(config['line_notify_token'], f"\n下班簽退成功!\n{records_str}")
    else:
        records_str = format_records(records, 'sign_out')
        send_line_notify(config['line_notify_token'], f"\n下班簽退成功!\n{records_str}")
    driver.quit()

def handle_automatic_sign_in_out(config):
    """
    Handles the automatic sign-in and sign-out process for each workday.
    Generates a random sign-in time, performs the sign-in and sign-out operations at the appropriate times, and sends notifications.
    Parameters:
        config: A dictionary containing configuration settings such as credentials and LINE Notify token.
    """
    # Generate a random sign-in time between 8:00 and 8:25 for the next day
    sign_in_time = (datetime.now() + timedelta(days=1)).replace(hour=8, minute=random.randint(0, 25), second=0, microsecond=0)
    sign_out_time = sign_in_time + timedelta(hours=9, minutes=5)

    # Skip Saturdays and Sundays
    if sign_in_time.weekday() in [5, 6]:
        return

    # Perform the sign-in operation at the sign-in time
    while datetime.now() < sign_in_time:
        time.sleep(60)
    driver = setup_driver()
    login(driver, config['psn_code'], config['password'])
    click_button(driver, "上班簽到")
    records = view_swipe_card_records(driver)
    if len(records) != 1:  # Retry if the number of records is not as expected
        click_button(driver, "上班簽到")
        records = view_swipe_card_records(driver)
        if len(records) != 1:  # Send failure message if still not as expected
            send_line_notify(config['line_notify_token'], "\n上班簽到失敗!\n請手動確認。")
        else:
            records_str = format_records(records, 'sign_in')  # Corrected 'sign_out' to 'sign_in'
            send_line_notify(config['line_notify_token'], f"\n上班簽到成功!\n{records_str}")
    else:
        records_str = format_records(records, 'sign_in')  # Corrected 'sign_out' to 'sign_in'
        send_line_notify(config['line_notify_token'], f"\n上班簽到成功!\n{records_str}")
    driver.quit()

    # Perform the sign-out operation at the sign-out time
    while datetime.now() < sign_out_time:
        time.sleep(60)
    driver = setup_driver()
    login(driver, config['psn_code'], config['password'])
    click_button(driver, "下班簽退")
    records = view_swipe_card_records(driver)
    if len(records) != 2:  # Retry if the number of records is not as expected
        click_button(driver, "下班簽退")
        records = view_swipe_card_records(driver)
        if len(records) != 2:  # Send failure message if still not as expected
            send_line_notify(config['line_notify_token'], "\n下班簽退失敗!\n請手動確認。")
        else:
            records_str = format_records(records, 'sign_out')
            send_line_notify(config['line_notify_token'], f"\n下班簽退成功!\n{records_str}")
    else:
        records_str = format_records(records, 'sign_out')
        send_line_notify(config['line_notify_token'], f"\n下班簽退成功!\n{records_str}")
    driver.quit()

def main():
    """
    The main function that orchestrates the entire automation process.
    It reads the configuration settings, checks if the current time is within work hours for immediate sign-out, and continuously handles automatic sign-in and sign-out.
    """
    with open(json_file_path, 'r', encoding="utf-8") as file:
        config = json.load(file)

    current_time = datetime.now()
    work_start_time = datetime.strptime("08:30", "%H:%M").time()
    work_end_time = datetime.strptime("17:30", "%H:%M").time()

    # Handle immediate sign-out if the script is run during work hours
    if work_start_time <= current_time.time() <= work_end_time:
        handle_immediate_sign_out(config, current_time)

    # Continuously handle automatic sign-in and sign-out for each workday
    while True:
        handle_automatic_sign_in_out(config)

if __name__ == "__main__":
    main()
