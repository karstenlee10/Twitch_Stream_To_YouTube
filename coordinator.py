from multiprocessing import Lock
from multiprocessing.synchronize import Lock as LockT
from pathlib import Path
import time
from typing import Any, Self, final
from typing_extensions import override

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

import config_tv as config
from logger import logger


CHROME_USER_DATA_DIR: Path = Path("~/AppData/Local/Google/User Data")


def _build_driver() -> WebDriver:
    options: Options = Options()  # Create Chrome options
    # Add user data directory to options
    options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")  # pyright: ignore[reportUnknownMemberType]
    # Add profile directory to options
    options.add_argument(f"profile-directory={config.Chrome_Profile}")  # pyright: ignore[reportUnknownMemberType]
    driver: WebDriver = webdriver.Chrome(options=options)  # Create Chrome driver
    return driver


def _edit_rtmp_key(
    driver: WebDriver, rtmp_key_select: str
) -> None:  # Function to edit RTMP key using Selenium WebDriver
    countfuckingshit = 0  # Counter for retry attempts
    while True:  # Infinite loop for retrying
        try:
            driver.find_element(
                By.XPATH, "//tp-yt-iron-icon[@icon='yt-icons:arrow-drop-down']"
            ).click()  # Clicking dropdown icon
            time.sleep(3)  # Waiting for 3 seconds
            if rtmp_key_select == "bkrtmp":  # Checking if RTMP key is "bkrtmp"
                xpath = (
                    "//ytls-menu-service-item-renderer[.//tp-yt-paper-item[contains(@aria-label, '"
                    + config.rtmpkeyname1
                    + " (')]]"
                )  # XPath for "bkrtmp"
                element2 = driver.find_element(
                    By.XPATH, xpath
                )  # Finding element for "bkrtmp"
                element2.click()  # Clicking the element
                time.sleep(7)  # Waiting for 7 seconds
            if rtmp_key_select == "defrtmp":  # Checking if RTMP key is "defrtmp"
                xpath = (
                    "//ytls-menu-service-item-renderer[.//tp-yt-paper-item[contains(@aria-label, '"
                    + config.rtmpkeyname
                    + " (')]]"
                )  # XPath for "defrtmp"
                element3 = driver.find_element(
                    By.XPATH, xpath
                )  # Finding element for "defrtmp"
                element3.click()  # Clicking the element
                time.sleep(7)  # Waiting for 7 seconds
            if config.disablechat == "True":  # Checking if chat should be disabled
                driver.find_element(
                    By.XPATH, "//ytcp-button[@id='edit-button']"
                ).click()  # Clicking edit button
                time.sleep(3)  # Waiting for 3 seconds
                driver.find_element(
                    By.XPATH, "//li[@id='customization']"
                ).click()  # Clicking customization tab
                time.sleep(2)  # Waiting for 2 seconds
                driver.find_element(
                    By.XPATH, "//*[@id='chat-enabled-checkbox']"
                ).click()  # Clicking chat-enabled checkbox
                time.sleep(1)  # Waiting for 1 second
                driver.find_element(
                    By.XPATH, "//ytcp-button[@id='save-button']"
                ).click()  # Clicking save button
            time.sleep(10)  # Waiting for 10 seconds
            logger.info(
                "RTMP key configuration updated successfully..."
            )  # Logging success message
            driver.quit()  # Quitting the driver
        except Exception as e:  # Handling exceptions
            logger.error(f"Error in edit_rtmp_key: {str(e)}")  # Logging error message
            driver.refresh()  # Refreshing the driver
            time.sleep(15)  # Waiting for 15 seconds
            countfuckingshit += 1  # Incrementing retry counter
            if countfuckingshit == 3:  # Checking if retry limit is reached
                logger.info(
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
            time.sleep(5)  # Waiting for 5 seconds
            driver.refresh()  # Refreshing the page
            time.sleep(30)  # Waiting for 30 seconds
            logger.info("Configuring RTMP key and chat settings...")
            _edit_rtmp_key(driver, rtmp_server)
