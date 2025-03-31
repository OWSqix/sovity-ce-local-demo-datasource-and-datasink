#!/usr/bin/env python
# run_backend.py

import os
import sys
import argparse
import subprocess
import signal
import time


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Data Space Connector Data Source/Sink Backend Services"
    )

    parser.add_argument(
        "--service",
        type=str,
        choices=["data_source", "data_sink", "all"],
        default="all",
        help="Service to run (data_source, data_sink, or all)"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="Set logging level (default: info)"
    )

    parser.add_argument(
        "--detailed-logs",
        action="store_true",
        help="Use detailed log format (including filename and line numbers)"
    )

    parser.add_argument(
        "--log-dir",
        type=str,
        default="./logs",
        help="Directory to store log files (default: ./logs)"
    )

    return parser.parse_args()


def is_in_backend_dir():
    current_dir = os.path.basename(os.path.abspath(os.getcwd()))
    return current_dir == "backend"


def get_module_path(service_type):
    if is_in_backend_dir():
        return f"{service_type}.main"
    else:
        return f"backend.{service_type}.main"


def run_service(service_type, args):
    os.makedirs(args.log_dir, exist_ok=True)

    module_path = get_module_path(service_type)

    cmd = [
        sys.executable, "-m", module_path,
        "--log-level", args.log_level,
        "--log-file", f"{args.log_dir}/{service_type}.log",
    ]

    if args.detailed_logs:
        cmd.append("--detailed-logs")

    print(f"[+] Starting {service_type} service...")
    print(f"    Module path: {module_path}")

    env = os.environ.copy()

    if is_in_backend_dir():
        current_path = os.path.abspath(os.getcwd())
        parent_path = os.path.dirname(current_path)
        env["PYTHONPATH"] = parent_path
        print(f"    PYTHONPATH set to: {parent_path}")
    else:
        env["PYTHONPATH"] = os.getcwd()
        print(f"    PYTHONPATH set to: {os.getcwd()}")

    return subprocess.Popen(
        cmd,
        env=env,
        stderr=subprocess.STDOUT
    )


def handle_signals(processes):
    def signal_handler(sig, frame):
        print("\n[!] Termination signal received. Shutting down services...")
        for proc in processes:
            if proc:
                proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    args = parse_args()
    processes = []

    try:
        print(f"[*] Running from: {'backend directory' if is_in_backend_dir() else 'project root'}")

        if args.service in ["data_source", "all"]:
            data_source_proc = run_service("data_source", args)
            processes.append(data_source_proc)

        if args.service in ["data_sink", "all"]:
            data_sink_proc = run_service("data_sink", args)
            processes.append(data_sink_proc)

        handle_signals(processes)

        print(f"[*] Services are running. (Log level: {args.log_level})")
        print(f"[*] Log files location: {args.log_dir}")
        print("[*] Press Ctrl+C to terminate...")

        while all(proc.poll() is None for proc in processes if proc):
            time.sleep(1)

        for proc in processes:
            if proc and proc.returncode:
                print(f"[!] Process terminated with code {proc.returncode}.")

    except Exception as e:
        print(f"[!] Error occurred: {str(e)}")
        for proc in processes:
            if proc:
                proc.terminate()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())