import json
import logging.config
from typing import Any

from selenium.webdriver.remote.remote_connection import LOGGER as _selenium_logger
from urllib3.connectionpool import log as _urllib_logger


with open("log.config.json") as log_config:
    logging_config: dict[str, Any] = json.load(log_config)  # pyright: ignore[reportExplicitAny,reportAny]


_selenium_logger.setLevel(logging.WARNING)
_urllib_logger.setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logging.config.dictConfig(logging_config)
