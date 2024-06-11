import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from AutomatedWorkClock import (
    validate_config,
    is_holiday,
    setup_driver,
    login,
    click_button,
    view_swipe_card_records,
    send_line_notify,
    format_records,
    perform_sign_in_out,
    handle_sign_in_out,
)
from selenium.webdriver.common.by import By


class TestSignInOut(unittest.TestCase):

    @patch("AutomatedWorkClock.holidays.Taiwan")
    def test_is_holiday(self, MockHolidays):
        MockHolidays.return_value = {datetime(2024, 1, 1)}
        self.assertTrue(is_holiday(datetime(2024, 1, 1)))
        self.assertFalse(is_holiday(datetime(2024, 1, 2)))

    def test_validate_config(self):
        valid_config = {
            "psn_code": "12345",
            "password": "password",
            "line_notify_token": "token",
            "sign_in_minute_start": 0,
            "sign_in_minute_end": 20,
        }
        self.assertIsNone(validate_config(valid_config))

        invalid_config_missing_key = {
            "psn_code": "12345",
            "password": "password",
            "line_notify_token": "token",
        }
        with self.assertRaises(ValueError):
            validate_config(invalid_config_missing_key)

        invalid_config_invalid_range = {
            "psn_code": "12345",
            "password": "password",
            "line_notify_token": "token",
            "sign_in_minute_start": 10,
            "sign_in_minute_end": 5,
        }
        with self.assertRaises(ValueError):
            validate_config(invalid_config_invalid_range)

    @patch("AutomatedWorkClock.webdriver.Chrome")
    @patch("AutomatedWorkClock.ChromeDriverManager.install")
    def test_setup_driver(self, mock_install, MockChrome):
        driver = setup_driver()
        self.assertIsInstance(driver, MagicMock)

    @patch("AutomatedWorkClock.WebDriverWait")
    def test_login(self, MockWebDriverWait):
        mock_driver = MagicMock()
        login(mock_driver, "psn_code", "password")
        mock_driver.get.assert_called_with(
            "https://eadm.ncku.edu.tw/welldoc/ncku/iftwd/signIn.php"
        )
        mock_driver.find_element.assert_any_call(By.ID, "psnCode")
        mock_driver.find_element.assert_any_call(By.ID, "password")

    @patch("AutomatedWorkClock.WebDriverWait")
    def test_click_button(self, MockWebDriverWait):
        mock_driver = MagicMock()
        mock_wait = MagicMock()
        MockWebDriverWait.return_value = mock_wait
        mock_wait.until.return_value = MagicMock()

        click_button(mock_driver, "button_text")
        mock_wait.until.assert_called_once()

    @patch("AutomatedWorkClock.WebDriverWait")
    def test_view_swipe_card_records(self, MockWebDriverWait):
        mock_driver = MagicMock()
        mock_wait = MagicMock()
        MockWebDriverWait.return_value = mock_wait
        mock_wait.until.return_value = MagicMock()

        records = view_swipe_card_records(mock_driver)
        self.assertIsInstance(records, list)

    @patch("AutomatedWorkClock.requests.post")
    def test_send_line_notify(self, mock_post):
        mock_post.return_value.status_code = 200
        self.assertTrue(send_line_notify("token", "message"))

        mock_post.return_value.status_code = 400
        self.assertFalse(send_line_notify("token", "message"))

    def test_format_records(self):
        records = [
            {
                "date": "2024-01-01",
                "weekDay": "Monday",
                "className": "Class A",
                "time": "08:00",
                "ip": "192.168.1.1",
            }
        ]
        formatted = format_records(records, "sign_in")
        self.assertIn("日期: 2024-01-01", formatted)

    @patch("AutomatedWorkClock.view_swipe_card_records")
    @patch("AutomatedWorkClock.click_button")
    @patch("AutomatedWorkClock.send_line_notify")
    def test_perform_sign_in_out(self, mock_notify, mock_click, mock_records):
        mock_driver = MagicMock()
        config = {
            "line_notify_token": "token",
        }
        mock_records.return_value = [
            {
                "date": "2024-01-01",
                "weekDay": "Monday",
                "className": "Class A",
                "time": "08:00",
                "ip": "192.168.1.1",
            }
        ]
        perform_sign_in_out(mock_driver, config, "sign_in")
        mock_click.assert_called()
        mock_notify.assert_called()

    @patch("AutomatedWorkClock.execute_sign_in_out")
    @patch("AutomatedWorkClock.setup_driver")
    @patch("AutomatedWorkClock.login")
    def test_handle_sign_in_out(self, mock_login, mock_setup, mock_execute):
        config = {
            "psn_code": "12345",
            "password": "password",
            "line_notify_token": "token",
            "sign_in_minute_start": 0,
            "sign_in_minute_end": 20,
        }
        handle_sign_in_out(config)
        mock_setup.assert_called()
        mock_login.assert_called()
        mock_execute.assert_called()


if __name__ == "__main__":
    unittest.main()
