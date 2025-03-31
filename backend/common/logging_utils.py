# backend/common/logging_utils.py

import logging
import os
import sys
from typing import Optional, Dict, Any

DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}


def get_log_level_from_env() -> int:
    log_level = os.environ.get("LOG_LEVEL", "info").lower()
    return LOG_LEVELS.get(log_level, logging.INFO)


def setup_logger(
        name: str,
        level: Optional[str] = None,
        log_file: Optional[str] = None,
        detailed_format: bool = False
) -> logging.Logger:

    log_level = LOG_LEVELS.get(level.lower(), None) if level else get_log_level_from_env()

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if logger.handlers:
        logger.handlers.clear()

    log_format = DETAILED_LOG_FORMAT if detailed_format else DEFAULT_LOG_FORMAT
    formatter = logging.Formatter(log_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class LogConfig:
    @staticmethod
    def get_config(
            app_name: str,
            log_level: Optional[str] = None,
            log_file: Optional[str] = None
    ) -> Dict[str, Any]:
        level = LOG_LEVELS.get(log_level.lower(), None) if log_level else get_log_level_from_env()

        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": DEFAULT_LOG_FORMAT,
                },
                "detailed": {
                    "format": DETAILED_LOG_FORMAT,
                },
            },
            "handlers": {
                "console": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "level": level,
                },
            },
            "loggers": {
                app_name: {"handlers": ["console"], "level": level, "propagate": False},
                "uvicorn": {"handlers": ["console"], "level": level},
                "uvicorn.access": {"handlers": ["console"], "level": level},
            },
        }

        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            config["handlers"]["file"] = {
                "formatter": "detailed",
                "class": "logging.FileHandler",
                "filename": log_file,
                "level": level,
            }
            config["loggers"][app_name]["handlers"].append("file")
            config["loggers"]["uvicorn"]["handlers"].append("file")
            config["loggers"]["uvicorn.access"]["handlers"].append("file")

        return config