#!/usr/bin/env python
# run_backend.py
"""
데이터스페이스 커넥터 데이터소스/싱크 백엔드 서비스를 실행하는 편리한 스크립트
"""

import os
import sys
import argparse
import subprocess
import signal
import time


def parse_args():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="데이터스페이스 커넥터 데이터소스/싱크 백엔드 서비스 실행"
    )

    parser.add_argument(
        "--service",
        type=str,
        choices=["data_source", "data_sink", "all"],
        default="all",
        help="실행할 서비스 (data_source, data_sink, 또는 all)"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="로그 레벨 설정 (기본값: info)"
    )

    parser.add_argument(
        "--detailed-logs",
        action="store_true",
        help="상세 로그 형식 사용 (파일명, 라인 번호 포함)"
    )

    parser.add_argument(
        "--log-dir",
        type=str,
        default="./logs",
        help="로그 파일 저장 디렉토리 (기본값: ./logs)"
    )

    return parser.parse_args()


def is_in_backend_dir():
    """현재 디렉토리가 'backend' 디렉토리인지 확인"""
    current_dir = os.path.basename(os.path.abspath(os.getcwd()))
    return current_dir == "backend"


def get_module_path(service_type):
    """실행 위치에 따라 올바른 모듈 경로 반환"""
    if is_in_backend_dir():
        # backend/ 디렉토리에서 실행 중이면 상대 경로 사용
        return f"{service_type}.main"
    else:
        # 프로젝트 루트에서 실행 중이면 전체 경로 사용
        return f"backend.{service_type}.main"


def run_service(service_type, args):
    """지정된 서비스를 실행"""
    # 로그 디렉토리가 없으면 생성
    os.makedirs(args.log_dir, exist_ok=True)

    # 실행 위치에 따른 모듈 경로 설정
    module_path = get_module_path(service_type)

    # 명령줄 파라미터 구성
    cmd = [
        sys.executable, "-m", module_path,
        "--log-level", args.log_level,
        "--log-file", f"{args.log_dir}/{service_type}.log",
    ]

    if args.detailed_logs:
        cmd.append("--detailed-logs")

    print(f"[+] {service_type} 서비스 시작 중...")
    print(f"    모듈 경로: {module_path}")

    # 환경 변수 설정 및 PYTHONPATH 조정
    env = os.environ.copy()

    # 실행 위치에 따라 적절한 PYTHONPATH 설정
    if is_in_backend_dir():
        # backend/ 디렉토리에서 실행할 때는 상위 디렉토리를 PYTHONPATH에 추가
        current_path = os.path.abspath(os.getcwd())
        parent_path = os.path.dirname(current_path)
        env["PYTHONPATH"] = parent_path
        print(f"    PYTHONPATH 설정: {parent_path}")
    else:
        # 프로젝트 루트에서 실행할 때는 현재 디렉토리를 PYTHONPATH에 추가
        env["PYTHONPATH"] = os.getcwd()
        print(f"    PYTHONPATH 설정: {os.getcwd()}")

    # 서브프로세스로 서비스 실행
    return subprocess.Popen(
        cmd,
        env=env,
        stderr=subprocess.STDOUT
    )


def handle_signals(processes):
    """신호 핸들러 설정"""

    def signal_handler(sig, frame):
        print("\n[!] 종료 신호 받음. 서비스를 종료합니다...")
        for proc in processes:
            if proc:
                proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """메인 함수"""
    args = parse_args()
    processes = []

    try:
        # 실행 정보 출력
        print(f"[*] 실행 위치: {'backend 디렉토리' if is_in_backend_dir() else '프로젝트 루트'}")

        # 요청된 서비스에 따라 실행
        if args.service in ["data_source", "all"]:
            data_source_proc = run_service("data_source", args)
            processes.append(data_source_proc)

        if args.service in ["data_sink", "all"]:
            data_sink_proc = run_service("data_sink", args)
            processes.append(data_sink_proc)

        # 신호 핸들러 설정
        handle_signals(processes)

        # 서비스 실행 중 메시지
        print(f"[*] 서비스가 실행 중입니다. (로그 레벨: {args.log_level})")
        print(f"[*] 로그 파일 위치: {args.log_dir}")
        print("[*] 종료하려면 Ctrl+C를 누르세요...")

        # 프로세스가 종료될 때까지 대기
        while all(proc.poll() is None for proc in processes if proc):
            time.sleep(1)

        # 비정상 종료 확인
        for proc in processes:
            if proc and proc.returncode:
                print(f"[!] 프로세스가 코드 {proc.returncode}로 종료되었습니다.")

    except Exception as e:
        print(f"[!] 오류 발생: {str(e)}")
        # 모든 프로세스 종료
        for proc in processes:
            if proc:
                proc.terminate()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())