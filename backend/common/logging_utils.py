# backend/common/logging_utils.py

import logging
import os
import sys
from typing import Optional, Dict, Any

# 로그 형식 정의
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

# 로그 레벨 매핑
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}


def get_log_level_from_env() -> int:
    """환경 변수에서 로그 레벨을 가져옵니다."""
    log_level = os.environ.get("LOG_LEVEL", "info").lower()
    return LOG_LEVELS.get(log_level, logging.INFO)


def setup_logger(
        name: str,
        level: Optional[str] = None,
        log_file: Optional[str] = None,
        detailed_format: bool = False
) -> logging.Logger:
    """
    지정된 이름으로 로거를 설정합니다.

    Args:
        name: 로거 이름
        level: 로그 레벨 ("debug", "info", "warning", "error", "critical")
        log_file: 로그를 저장할 파일 경로 (None인 경우 콘솔에만 출력)
        detailed_format: 상세 로그 형식 사용 여부

    Returns:
        설정된 로거 인스턴스
    """
    # 로그 레벨 결정 (인자 우선, 없으면 환경 변수, 기본값은 INFO)
    log_level = LOG_LEVELS.get(level.lower(), None) if level else get_log_level_from_env()

    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 이미 핸들러가 설정되어 있으면 중복 방지를 위해 제거
    if logger.handlers:
        logger.handlers.clear()

    # 로그 포맷 설정
    log_format = DETAILED_LOG_FORMAT if detailed_format else DEFAULT_LOG_FORMAT
    formatter = logging.Formatter(log_format)

    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 추가 (옵션)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class LogConfig:
    """FastAPI 애플리케이션을 위한 로깅 설정"""

    @staticmethod
    def get_config(
            app_name: str,
            log_level: Optional[str] = None,
            log_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        FastAPI의 로깅 설정을 반환합니다.

        Args:
            app_name: 애플리케이션 이름
            log_level: 로그 레벨
            log_file: 로그 파일 경로

        Returns:
            로깅 설정 딕셔너리
        """
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

        # 파일 로깅 설정 (옵션)
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