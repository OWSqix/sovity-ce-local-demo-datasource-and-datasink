# backend/common/cli_parser.py

import argparse
from typing import Dict, Any, Optional


def parse_arguments() -> Dict[str, Any]:
    """
    명령줄 인자를 파싱하고 설정 딕셔너리를 반환합니다.

    Returns:
        Dict[str, Any]: 설정 옵션이 포함된 딕셔너리
    """
    parser = argparse.ArgumentParser(description="Data Space Connector Data Source/Sink Backend")

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="로그 레벨 설정 (기본값: info)"
    )

    parser.add_argument(
        "--log-file",
        type=str,
        help="로그를 저장할 파일 경로 (기본값: 콘솔 출력만)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="서비스를 바인딩할 호스트 (기본값: 127.0.0.1)"
    )

    parser.add_argument(
        "--port",
        type=int,
        help="서비스 포트 (기본값: 데이터 소스 - 8003, 데이터 싱크 - 8002)"
    )

    parser.add_argument(
        "--detailed-logs",
        action="store_true",
        help="파일명과 라인 번호를 포함한 상세 로그 출력"
    )

    return vars(parser.parse_args())


def get_service_settings(service_type: str, cli_args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    서비스 유형에 기반한 설정을 반환합니다.

    Args:
        service_type: 서비스 유형 ("data_source" 또는 "data_sink")
        cli_args: 명령줄 인자 딕셔너리 (None인 경우 자동으로 파싱)

    Returns:
        설정 딕셔너리
    """
    if cli_args is None:
        cli_args = parse_arguments()

    # 서비스 유형에 따른 기본 포트 설정
    default_port = 8003 if service_type == "data_source" else 8002

    # 로그 파일 경로 설정 (지정되지 않은 경우)
    if cli_args.get("log_file") is None:
        log_dir = "./logs"
        cli_args["log_file"] = f"{log_dir}/{service_type}.log"

    # 포트 설정 (명령줄에서 지정되지 않은 경우 기본값 사용)
    if cli_args.get("port") is None:
        cli_args["port"] = default_port

    return cli_args