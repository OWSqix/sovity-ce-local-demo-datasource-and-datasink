import argparse
from typing import Dict, Any, Optional


def parse_arguments() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description="Data Space Connector Data Source/Sink Backend")

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="Set logging level (default: info)"
    )

    parser.add_argument(
        "--log-file",
        type=str,
        help="File path to save logs (default: console output only)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the service (default: 127.0.0.1)"
    )

    parser.add_argument(
        "--port",
        type=int,
        help="Service port (default: data source - 8003, data sink - 8002)"
    )

    parser.add_argument(
        "--detailed-logs",
        action="store_true",
        help="Enable detailed logging with filename and line numbers"
    )

    return vars(parser.parse_args())


def get_service_settings(service_type: str, cli_args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if cli_args is None:
        cli_args = parse_arguments()

    default_port = 8003 if service_type == "data_source" else 8002

    if cli_args.get("log_file") is None:
        log_dir = "./logs"
        cli_args["log_file"] = f"{log_dir}/{service_type}.log"

    if cli_args.get("port") is None:
        cli_args["port"] = default_port

    return cli_args