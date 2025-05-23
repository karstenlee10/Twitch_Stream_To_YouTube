import json
import logging.config
from typing import Any


with open("log.config.json") as log_config:
    logging_config: dict[str, Any] = json.load(log_config)  # pyright: ignore[reportExplicitAny,reportAny]

logger = logging.getLogger(__name__)
logging.config.dictConfig(logging_config)
