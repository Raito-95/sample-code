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
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import holidays
from typing import List, Dict, Any, Tuple

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

json_file_path = os.path.join(os.path.dirname(__file__), "credentials.json")
tw_holidays = holidays.Taiwan()


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration settings"""
    required_keys = [
        "psn_code",
        "password",
        "line_notify_token",
        "sign_in_minute_start",
        "sign_in_minute_end",
    ]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Configuration missing '{key}'.")

    if not (0 <= config["sign_in_minute_start"] < config["sign_in_minute_end"] <= 20):
        raise ValueError("Invalid sign-in minute range in configuration.")


def is_holiday(date: datetime) -> bool:
    """Check if the given date is a holiday in Taiwan"""
    return date in tw_holidays


def setup_driver() -> Tuple[webdriver.Chrome, str]:
    """Set up Chrome WebDriver in headless mode with GPU acceleration disabled and return the driver and its version"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )
        driver_version = driver.capabilities["chrome"]["chromedriverVersion"].split(
            " "
        )[0]
        print(f"使用的 ChromeDriver 版本: {driver_version}")
    except Exception as e:
        logging.error("Failed to initialize browser driver: %s", e)
        raise
    return driver, driver_version


def login(driver: webdriver.Chrome, psn_code: str, password: str) -> None:
    """Log in to the website using provided credentials"""
    driver.get("https://eadm.ncku.edu.tw/welldoc/ncku/iftwd/signIn.php")
    driver.find_element(By.ID, "psnCode").send_keys(psn_code)
    driver.find_element(By.ID, "password").send_keys(password)

    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
    except TimeoutException:
        pass


def click_button(
    driver: webdriver.Chrome, button_text: str, wait_time: int = 10
) -> None:
    """Wait for a button with specified text to be clickable, then click it"""
    try:
        wait = WebDriverWait(driver, wait_time)
        button_xpath = f"//button[contains(text(), '{button_text}')]"
        button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
        button.click()
        time.sleep(5)
    except TimeoutException as e:
        logging.error("Failed to click button '%s': %s", button_text, e)
        raise


def view_swipe_card_records(
    driver: webdriver.Chrome, wait_time: int = 10
) -> List[Dict[str, str]]:
    """Click button to view today's swipe card records and extract data"""
    click_button(driver, "查看本日刷卡紀錄", wait_time=wait_time)

    try:
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
                    "ip": cols[4].text,
                }
                records.append(record)
        return records
    except TimeoutException as e:
        logging.error("Failed to load swipe card record table: %s", e)
        raise


def send_line_notify(token: str, message: str) -> bool:
    """Send notification message via LINE Notify"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"message": message}
    try:
        response = requests.post(
            "https://notify-api.line.me/api/notify",
            headers=headers,
            data=data,
            timeout=10,
        )
        if response.status_code != 200:
            logging.error("Failed to send LINE Notify message: %s", response.text)
            return False
        return True
    except requests.RequestException as e:
        logging.error("LINE Notify request failed: %s", e)
        return False


def format_records(records: List[Dict[str, str]], sign_type: str) -> str:
    """Format swipe card record list to string for display or messaging"""
    if sign_type not in ["sign_in", "sign_out"]:
        return "Invalid sign-in type."
    if not records:
        return "No records found."
    record = records[0] if sign_type == "sign_in" else records[-1]
    return (
        f"日期: {record['date']}\n"
        f"星期: {record['weekDay']}\n"
        f"班別: {record['className']}\n"
        f"時間: {record['time']}\n"
        f"IP: {record['ip']}\n"
    )


def perform_sign_in_out(
    driver: webdriver.Chrome, config: Dict[str, Any], sign_type: str
) -> None:
    """Perform sign-in or sign-out operation and send notification"""
    button_text = "上班簽到" if sign_type == "sign_in" else "下班簽退"
    click_button(driver, button_text)
    records = view_swipe_card_records(driver)
    expected_records = 1 if sign_type == "sign_in" else 2
    if len(records) != expected_records:
        click_button(driver, button_text)
        records = view_swipe_card_records(driver)
        if len(records) != expected_records:
            send_line_notify(
                config["line_notify_token"], f"\n{button_text}失敗!\n請手動確認。"
            )
            return
    records_str = format_records(records, sign_type)
    send_line_notify(
        config["line_notify_token"], f"\n{button_text}成功!\n{records_str}"
    )


def execute_sign_in_out(sign_type: str, config: Dict[str, Any]) -> None:
    """Execute sign-in or sign-out operation"""
    logging.info(f"開始執行{sign_type}操作")
    driver, driver_version = setup_driver()
    try:
        login(driver, config["psn_code"], config["password"])
        perform_sign_in_out(driver, config, sign_type)
    finally:
        driver.quit()
        logging.info("瀏覽器已關閉")


def handle_sign_in_out(config: Dict[str, Any]) -> None:
    """Handle sign-in and sign-out process based on current time and work schedule"""
    current_time = datetime.now()
    sign_in_hour = 8

    def get_sign_times(sign_in_minute: int) -> Tuple[datetime, datetime]:
        sign_in_time = datetime(
            current_time.year,
            current_time.month,
            current_time.day,
            sign_in_hour,
            sign_in_minute,
        )
        sign_out_time = sign_in_time + timedelta(hours=9, minutes=5)
        return sign_in_time, sign_out_time

    default_sign_in_time, default_sign_out_time = get_sign_times(
        config["sign_in_minute_start"]
    )

    logging.info(f"上班時間: {default_sign_in_time}")
    logging.info(f"下班時間: {default_sign_out_time}")

    def wait_until(target_time: datetime) -> None:
        while datetime.now() < target_time:
            time.sleep(60)

    if current_time < default_sign_in_time:
        logging.info("當前時間早於上班時間，等待中...")
        wait_until(default_sign_in_time)
        logging.info("已到達上班時間，進行簽到...")
        execute_sign_in_out("sign_in", config)
        logging.info("等待簽退時間...")
        wait_until(default_sign_out_time)
        logging.info("已到達簽退時間，進行簽退...")
        execute_sign_in_out("sign_out", config)

    elif default_sign_in_time <= current_time < default_sign_out_time:
        logging.info("當前時間在上班時間範圍內，等待輸入上班時間...")
        while True:
            sign_in_minute_input = input("請輸入上班時間的分鐘數(格式:MM): ")
            try:
                sign_in_minute = int(sign_in_minute_input)
                if (
                    config["sign_in_minute_start"]
                    <= sign_in_minute
                    < config["sign_in_minute_end"]
                ):
                    logging.info(
                        "已輸入有效的上班時間，程式現在將進入等待狀態，直到簽退時間。"
                    )
                    break
                else:
                    logging.warning(
                        f"請輸入{config['sign_in_minute_start']}到{config['sign_in_minute_end'] - 1}之間的分鐘數"
                    )
            except ValueError:
                logging.warning("分鐘數格式不正確，請重新輸入。")

        sign_in_time, sign_out_time = get_sign_times(sign_in_minute)
        logging.info(f"今日上班時間: {sign_in_time}")
        logging.info(f"今日下班時間: {sign_out_time}")

        logging.info("等待簽退時間...")
        wait_until(sign_out_time)
        logging.info("已到達簽退時間，進行簽退...")
        execute_sign_in_out("sign_out", config)

    while True:
        next_workday = current_time + timedelta(days=1)
        while next_workday.weekday() in [5, 6] or is_holiday(next_workday):
            next_workday += timedelta(days=1)
        sign_in_minute = random.randint(
            config["sign_in_minute_start"], config["sign_in_minute_end"] - 1
        )
        sign_in_time = next_workday.replace(
            hour=sign_in_hour, minute=sign_in_minute, second=0, microsecond=0
        )
        sign_out_time = sign_in_time + timedelta(hours=9, minutes=5)

        logging.info(f"下一個工作日上班時間: {sign_in_time}")
        logging.info(f"下一個工作日下班時間: {sign_out_time}")

        logging.info("等待簽到時間...")
        wait_until(sign_in_time)
        logging.info("已到達上班時間，進行簽到...")
        execute_sign_in_out("sign_in", config)

        logging.info("等待簽退時間...")
        wait_until(sign_out_time)
        logging.info("已到達簽退時間，進行簽退...")
        execute_sign_in_out("sign_out", config)
        current_time = datetime.now()
        logging.info("------------------------------")


def main() -> None:
    """Main function, read configuration and start sign-in and sign-out process"""
    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            config = json.load(file)
        validate_config(config)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        logging.error("Error reading or validating configuration: %s", e)
        return

    handle_sign_in_out(config)


if __name__ == "__main__":
    main()
