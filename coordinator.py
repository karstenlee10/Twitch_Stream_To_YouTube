from multiprocessing import Lock
from multiprocessing.synchronize import Lock as LockT
from pathlib import Path
import time
from typing import Any, Self, final
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC  # Importing expected_conditions for waiting conditions
from selenium.webdriver.support.wait import WebDriverWait
from typing_extensions import override

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

import config_tv as config
from logger_config import check_tv_logger as logging


CHROME_USER_DATA_DIR: Path = Path("~/AppData/Local/Google/User Data")


def _build_driver() -> WebDriver:
    options: Options = Options()  # Create Chrome options
    # Add user data directory to options
    options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")  # pyright: ignore[reportUnknownMemberType]
    # Add profile directory to options
    options.add_argument(f"profile-directory={config.Chrome_Profile}")  # pyright: ignore[reportUnknownMemberType]
    driver: WebDriver = webdriver.Chrome(options=options)  # Create Chrome driver
    return driver


# moved the function here to avoid circular imports
def _edit_rtmp_key(
    driver: WebDriver, rtmp_server: str
) -> None:  # Function to edit RTMP key using Selenium WebDriver
    try_count = 0  # Counter for retry attempts
    while True:  # Infinite loop for retrying
        try:
            driver.find_element(By.XPATH, "//tp-yt-paper-radio-button[2]").click()
            time.sleep(5)
            driver.find_element(By.XPATH, "//tp-yt-iron-icon[@icon='yt-icons:arrow-drop-down']").click()  # Clicking dropdown icon
            time.sleep(3)  # Waiting for 3 seconds
            if rtmp_server == "bkrtmp":  # Checking if RTMP key is "bkrtmp"
                element2 = driver.find_element(By.XPATH, "//ytls-menu-service-item-renderer[.//tp-yt-paper-item[contains(@aria-label, '" + config.rtmpkeyname1 + " (')]]")  # Finding element for "bkrtmp"
                element2.click()  # Clicking the element
                time.sleep(7)  # Waiting for 7 seconds
            if rtmp_server == "defrtmp":  # Checking if RTMP key is "defrtmp"
                element3 = driver.find_element(By.XPATH, "//ytls-menu-service-item-renderer[.//tp-yt-paper-item[contains(@aria-label, '" + config.rtmpkeyname + " (')]]")  # Finding element for "defrtmp"
                element3.click()  # Clicking the element
                time.sleep(7)  # Waiting for 7 seconds
            if config.disablechat == "True":  # Checking if chat should be disabled
                driver.find_element(By.XPATH, "//ytcp-button[@id='edit-button']").click()  # Clicking edit button
                time.sleep(3)  # Waiting for 3 seconds
                driver.find_element(By.XPATH, "//li[@id='customization']").click()  # Clicking customization tab
                time.sleep(2)  # Waiting for 2 seconds
                driver.find_element(By.XPATH, "//*[@id='chat-enabled-checkbox']").click()  # Clicking chat-enabled checkbox
                time.sleep(1)  # Waiting for 1 second
                driver.find_element(By.XPATH, "//ytcp-button[@id='save-button']").click()  # Clicking save button
            if config.disablechat == "False":  # Checking if chat should be replayable
                driver.find_element(By.XPATH, "//ytcp-button[@id='edit-button']").click()  # Clicking edit button
                time.sleep(3)  # Waiting for 3 seconds
                driver.find_element(By.XPATH, "//li[@id='customization']").click()  # Clicking customization tab
                time.sleep(2)  # Waiting for 2 seconds
                driver.find_element(By.XPATH, "//ytcp-checkbox-lit/div/div[1]").click()  # Clicking chat-enabled checkbox
                time.sleep(1)  # Waiting for 1 second
                driver.find_element(By.XPATH, "//ytcp-button[@id='save-button']").click()  # Clicking save button
            while True:
                try:
                    _ = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/ytcp-app/ytcp-toast-manager/tp-yt-paper-toast"))
                    )
                    logging.info("Toast notification appeared")
                    break
                except TimeoutException:
                    logging.info("Toast notification not found, continuing to wait...")
            logging.info("RTMP key configuration updated successfully...")  # Logging success message
        except Exception as e:  # Handling exceptions
            logging.error(f"Error in edit_rtmp_key: {str(e)}")  # Logging error message
            driver.refresh()  # Refreshing the driver
            time.sleep(15)  # Waiting for 15 seconds
            try_count += 1  # Incrementing retry counter
            if try_count >= 3:  # Checking if retry limit is reached
                logging.info(
                    "edit rtmp key fail shutdown script"
                )  # Logging failure message
                exit()  # Exiting the script
        finally:
            break  # Breaking the loop


@final
class SingletonMeta(type):
    _instances: dict[Any, Any] = {}  # pyright:ignore[reportExplicitAny]

    @override
    def __call__[T](cls, *args: list[Any], **kwargs: dict[Any, T | Any]) -> T:  # pyright:ignore[reportExplicitAny]
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]  # pyright:ignore[reportAny]


def load_api(auth_url: str, has_brand: bool) -> None:
    coordinator: Coordinator = Coordinator()
    coordinator.load_api(auth_url, has_brand)


class Coordinator(metaclass=SingletonMeta):
    _instance: Self | None = None

    def __init__(self) -> None:
        self._lock: LockT = Lock()

    def load_api(self, url: str, has_brand: bool) -> None:
        """
        blocks until the lock is aquired to do work.
        TODO: this is only used in `flow.py`, what does it actually do?
        """
        # blocks until lock is available
        with self._lock, _build_driver() as driver:
            driver.get(url)  # Open URL in Chrome
            time.sleep(3)  # Sleep for 3 seconds
            # Get brand account name
            nameofaccount: str = (
                f"//div[contains(text(),'{config.brandaccname}')]"
                if has_brand
                else f"//div[contains(text(),'{config.accountname}')]"
            )
            button_element = driver.find_element(
                "xpath", nameofaccount
            )  # Find account button
            button_element.click()  # Click account button
            time.sleep(3)  # Sleep for 3 seconds
            element = driver.find_element(
                "xpath",
                "(//button[@jsname='LgbsSe' and contains(@class, 'VfPpkd-LgbsSe-OWXEXe-INsAgc')])[2]",
            )  # Find button element
            element.click()  # Click button element

            time.sleep(5)  # Sleep for 5 seconds

    def setup_stream_settings(self, stream_url: str, rtmp_server: str) -> None:
        with self._lock, _build_driver() as driver:
            url_to_live = f"https://studio.youtube.com/video/{stream_url}/livestreaming"  # Constructing URL to live stream
            driver.get(url_to_live)  # Navigating to URL
            while True:
                   try:
                       _ = WebDriverWait(driver, 30).until(
                           EC.presence_of_element_located((By.XPATH, '/html/body/ytcp-app/ytls-live-streaming-section/ytls-core-app/div/div[2]/div/ytls-live-dashboard-page-renderer/div[1]/div[1]/ytls-live-control-room-renderer/div[1]/div/div/ytls-broadcast-metadata/div[2]/ytcp-button/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]'))
                       )
                       break
                   except TimeoutException:
                       logging.info("Element not found after 30s, refreshing page...")
                       driver.refresh()
                       time.sleep(2)
            logging.info("Configuring RTMP key and chat settings...")
            _edit_rtmp_key(driver, rtmp_server)
