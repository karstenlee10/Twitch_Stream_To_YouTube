from multiprocessing import Lock
from multiprocessing.synchronize import Lock as LockT
from pathlib import Path
import time
from typing import Any, Self, final
from typing_extensions import override

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

import config_tv as config


CHROME_USER_DATA_DIR: Path = Path("~/AppData/Local/Google/User Data")


def _build_driver() -> WebDriver:
    options: Options = Options()  # Create Chrome options
    # Add user data directory to options
    options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")  # pyright: ignore[reportUnknownMemberType]
    # Add profile directory to options
    options.add_argument(f"profile-directory={config.Chrome_Profile}")  # pyright: ignore[reportUnknownMemberType]
    driver: WebDriver = webdriver.Chrome(options=options)  # Create Chrome driver
    return driver


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
        with self._lock:
            driver: WebDriver = _build_driver()
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
            driver.quit()  # Quit Chrome driver
