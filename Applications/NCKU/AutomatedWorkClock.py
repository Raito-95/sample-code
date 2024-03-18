import os
import sys
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
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import holidays

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
tw_holidays = holidays.Taiwan()

class SignInOutAutomation:
    """
    A class for automating sign-in and sign-out processes.

    Attributes:
        config_path (str): Path to the configuration file.
        config (dict): Configuration dictionary.
        driver (webdriver): Web browser automation driver.
    """
    def __init__(self, config_path):
        """
        Initializes the SignInOutAutomation class.

        Args:
            config_path (str): Path to the configuration file.
        """
        self.config = self.load_config(config_path)
        self.validate_config()
        self.driver = self.setup_driver()

    def load_config(self, config_path):
        """
        Loads the configuration file.

        Args:
            config_path (str): Path to the configuration file.

        Returns:
            dict: Configuration dictionary.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            json.JSONDecodeError: If the configuration file is not in a valid JSON format.
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error("讀取或驗證配置文件時發生錯誤：%s", e)
            sys.exit(1)

    def validate_config(self):
        """
        Validates the necessary keys in the configuration.

        Raises:
            ValueError: If essential keys are missing in the configuration.
        """
        required_keys = ['psn_code', 'password', 'line_notify_token', 'sign_in_minute_start', 'sign_in_minute_end']
        for key in required_keys:
            if key not in self.config:
                logging.error("配置文件中缺少 '%s' 鍵。", key)
                sys.exit(1)

        if not (0 <= self.config['sign_in_minute_start'] < self.config['sign_in_minute_end'] <= 60):
            logging.error("配置文件中的簽到時間範圍無效。")
            sys.exit(1)

    def setup_driver(self):
        """
        Sets up the WebDriver.

        Returns:
            webdriver: The initialized WebDriver instance.

        Raises:
            WebDriverException: If there is an issue setting up the WebDriver.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            return driver
        except WebDriverException as e:
            logging.error("WebDriver設置失敗：%s", e)
            sys.exit(1)

    def login(self):
        """
        Logs into the specified website.

        Raises:
            WebDriverException: If there is an issue during the login process.
        """
        try:
            self.driver.get("https://eadm.ncku.edu.tw/welldoc/ncku/iftwd/signIn.php")
            self.driver.find_element(By.ID, "psnCode").send_keys(self.config['psn_code'])
            self.driver.find_element(By.ID, "password").send_keys(self.config['password'])
            WebDriverWait(self.driver, 10).until(EC.alert_is_present()).accept()
        except WebDriverException as e:
            logging.error("登入失敗：%s", e)
            self.driver.quit()
            sys.exit(1)

    def perform_action(self, action):
        """
        Performs the sign-in or sign-out action.

        Args:
            action (str): The action type ('sign_in' or 'sign_out').

        Returns:
            bool: True if the action was successful, False otherwise.
        """
        actions = {
            'sign_in': "上班簽到",
            'sign_out': "下班簽退"
        }
        button_text = actions.get(action, '')
        if button_text:
            if self.click_button(button_text):
                records = self.view_swipe_card_records()
                if not records:
                    logging.error("%s 失敗：未找到記錄。", button_text)
                    return False
                self.send_line_notify(f"{button_text}成功!\n{self.format_records(records, action)}")
                return True

            return False

        logging.error("指定的操作無效。")
        return False

    def click_button(self, button_text, wait_time=10):
        """
        Clicks a button on the web page that matches the given text.

        Args:
            button_text (str): The text of the button to click.
            wait_time (int): The maximum time to wait for the button to be clickable.

        Returns:
            bool: True if the button was clicked successfully, False otherwise.

        Raises:
            WebDriverException: If the button could not be clicked.
        """
        try:
            wait = WebDriverWait(self.driver, wait_time)
            button_xpath = f"//button[contains(text(), '{button_text}')]"
            button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
            button.click()
            time.sleep(1)
        except WebDriverException as e:
            logging.error("點擊按鈕 '%s' 失敗：%s", button_text, e)
            return False
        return True

    def view_swipe_card_records(self, wait_time=10):
        """
        Views and extracts the swipe card records from the web page.

        Args:
            wait_time (int): The maximum time to wait for the records to be visible.

        Returns:
            list[dict]: A list of dictionaries containing the swipe card records.

        Raises:
            WebDriverException: If the swipe card records could not be retrieved.
        """
        try:
            wait = WebDriverWait(self.driver, wait_time)
            table_xpath = "//table[@id='checkinList']"
            table = wait.until(EC.visibility_of_element_located((By.XPATH, table_xpath)))
            rows = table.find_elements(By.TAG_NAME, "tr")
            records = []
            for row in rows[1:]:
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
        except WebDriverException as e:
            logging.error("查看刷卡記錄失敗：%s", e)
            return []

    def send_line_notify(self, message):
        """
        Sends a notification message via LINE Notify.

        Args:
            message (str): The message to send.

        Returns:
            bool: True if the message was sent successfully, False otherwise.

        Raises:
            requests.RequestException: If there is an issue sending the notification.
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.config['line_notify_token']}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {"message": message}
            response = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data, timeout=10)
            if response.status_code != 200:
                logging.error("LINE通知發送失敗：%s", response.text)
                return False
        except requests.RequestException as e:
            logging.error("LINE通知錯誤：%s", e)
            return False
        return True

    def format_records(self, records, sign_type):
        """
        Formats the swipe card records into a string for display or messaging.

        Args:
            records (list[dict]): The list of swipe card records to format.
            sign_type (str): The type of sign action ('sign_in' or 'sign_out').

        Returns:
            str: Formatted string of the latest (or earliest) record based on the sign_type.
        """
        if sign_type not in ['sign_in', 'sign_out']:
            logging.error("指定的簽到簽退類型無效。")
            return "無效的簽到簽退類型。"

        if not records:
            return "未找到記錄。"

        record = records[0] if sign_type == 'sign_in' else records[-1]
        return (f"日期: {record['date']}\n"
                f"星期: {record['weekDay']}\n"
                f"班別: {record['className']}\n"
                f"時間: {record['time']}\n"
                f"IP: {record['ip']}")

    def perform_sign_in_out(self, sign_type):
        """
        Performs the sign-in or sign-out operation and sends a notification about the action.

        This method handles the actual clicking of the sign-in or sign-out button on the web interface,
        checks for the presence of record entries to confirm the action, and sends a notification
        through LINE Notify about the success or failure of the action.

        Args:
            sign_type (str): The type of action to perform ('sign_in' or 'sign_out').

        Returns:
            bool: True if the operation and notification sending were successful, False otherwise.

        Raises:
            WebDriverException: If there is an issue with the web driver operations.
        """
        actions = {
            'sign_in': "上班簽到",
            'sign_out': "下班簽退"
        }
        button_text = actions.get(sign_type, '')
        if button_text:
            self.login()
            time.sleep(5)

            if self.click_button(button_text):
                records = self.view_swipe_card_records()
                if not records:
                    logging.error("%s 失敗：未找到記錄。", button_text)
                    return False

                self.send_line_notify(f"{button_text}成功!\n{self.format_records(records, sign_type)}")
                return True

            logging.error("%s 操作失败。", button_text)
            return False

        logging.error("未知的簽到簽退操作：%s", sign_type)
        return False

    def handle_sign_in_out(self):
        """
        Handles the automated sign-in and sign-out process based on the configured schedule.
        """
        current_time = datetime.now()
        sign_in_hour = 8

        default_sign_in_time = datetime(current_time.year, current_time.month, current_time.day, sign_in_hour, self.config['sign_in_minute_start'])
        default_sign_out_time = default_sign_in_time + timedelta(hours=9, minutes=5)

        logging.info("預設簽到時間：%s", default_sign_in_time)
        logging.info("預設簽退時間：%s", default_sign_out_time)

        if current_time < default_sign_in_time:
            logging.info("當前時間早於上班時間，等待中...")
            self.wait_until_time(default_sign_in_time)
            logging.info("達到預設簽到時間，開始簽到流程。")
            self.perform_sign_in_out("sign_in")
            logging.info("簽到流程結束。")

            actual_sign_out_time = default_sign_in_time + timedelta(hours=9, minutes=5)
            logging.info("根據預設簽到時間，預計簽退時間為：%s", actual_sign_out_time)

            self.wait_until_time(actual_sign_out_time)
            logging.info("達到預計簽退時間，開始簽退流程。")
            self.perform_sign_in_out("sign_out")
            logging.info("簽退流程結束。")
        elif default_sign_in_time <= current_time < default_sign_out_time:
            logging.info("當前時間在上班時間範圍內。")
            sign_in_time = self.prompt_for_actual_sign_in_time(sign_in_hour)
            logging.info("實際簽到時間已設定為：%s。", sign_in_time)

            actual_sign_out_time = sign_in_time + timedelta(hours=9, minutes=5)
            logging.info("根據實際簽到時間，預計簽退時間為：%s", actual_sign_out_time)

            self.wait_until_time(actual_sign_out_time)
            logging.info("達到預計簽退時間，開始簽退流程。")
            self.perform_sign_in_out("sign_out")
            logging.info("簽退流程結束。")

        while True:
            next_workday = self.calculate_next_workday(current_time + timedelta(days=1))
            next_sign_in_time = next_workday.replace(hour=sign_in_hour, minute=random.randint(self.config['sign_in_minute_start'], self.config['sign_in_minute_end'] - 1))
            next_sign_out_time = next_sign_in_time + timedelta(hours=9, minutes=5)

            logging.info("下一個工作日簽到時間：%s", next_sign_in_time)
            logging.info("下一個工作日簽退時間：%s", next_sign_out_time)

            self.wait_until_time(next_sign_in_time)
            logging.info("達到下一個工作日簽到時間，開始簽到流程。")
            self.perform_sign_in_out("sign_in")
            logging.info("簽到流程結束。")

            self.wait_until_time(next_sign_out_time)
            logging.info("達到下一個工作日簽退時間，開始簽退流程。")
            self.perform_sign_in_out("sign_out")
            logging.info("簽退流程結束。")

            current_time = datetime.now()

    def prompt_for_actual_sign_in_time(self, sign_in_hour):
        """
        Prompts the user for the actual sign-in time if the current time is within working hours.

        Args:
            sign_in_hour (int): The hour at which the workday starts.

        Returns:
            datetime: The actual sign-in time input by the user.
        """
        while True:
            sign_in_minute_input = input("請輸入上班時間的分鐘數(格式:MM): ")
            try:
                sign_in_minute = int(sign_in_minute_input)
                if self.config['sign_in_minute_start'] <= sign_in_minute < self.config['sign_in_minute_end']:
                    return datetime.now().replace(hour=sign_in_hour, minute=sign_in_minute, second=0, microsecond=0)
                print(f"請輸入有效的時間範圍：{self.config['sign_in_minute_start']}至{self.config['sign_in_minute_end'] - 1}之間的分鐘數")
            except ValueError:
                print("輸入格式不正確，請重新輸入。")

    def wait_until_time(self, target_time):
        """
        Waits until the specified target time.

        Args:
            target_time (datetime): The time to wait until.
        """
        while datetime.now() < target_time:
            time.sleep(60)

    def calculate_next_workday(self, current_date):
        """
        Calculates the next workday, skipping weekends and holidays.

        Args:
            current_date (datetime): The current date from which to calculate the next workday.

        Returns:
            datetime: The date of the next workday.
        """
        next_workday = current_date + timedelta(days=1)
        while next_workday.weekday() in [5, 6] or next_workday in tw_holidays:
            next_workday += timedelta(days=1)
        return next_workday

    def close_driver(self):
        """
        Closes the web browser and quits the WebDriver.
        """
        if self.driver:
            self.driver.quit()
            logging.info("瀏覽器已關閉。")

def main():
    """
    The main entry point of the program.

    This function loads the configuration, initializes the automation class, and starts the
    sign-in and sign-out process based on the current time and configured schedule. It ensures
    that the web driver is properly closed after the operations are completed.
    """
    config_path = os.path.join(os.path.dirname(__file__), '_credentials.json')
    automation = SignInOutAutomation(config_path)

    try:
        automation.handle_sign_in_out()
    finally:
        automation.close_driver()

if __name__ == "__main__":
    main()
