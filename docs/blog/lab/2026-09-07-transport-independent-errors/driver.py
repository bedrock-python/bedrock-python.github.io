"""Ask the same use case over HTTP and over gRPC, and print what each transport said."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from importlib.metadata import version

import grpc
import httpx

CASES = ["missing", "paid", "forbidden", "provider", "ledger", "unexpected", "ok"]
SERVICE = "lab.Orders"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def log(msg: str) -> None:
    print(msg, flush=True)


def http_call(base: str, case: str) -> tuple[str, str]:
    with httpx.Client() as client:
        response = client.post(f"{base}/orders/{case}/pay", timeout=5)
        try:
            body = response.json()
        except ValueError:
            body = response.text
        if isinstance(body, dict):
            shown = {k: body[k] for k in ("title", "status", "code", "detail", "type") if k in body}
        else:
            shown = body
        return str(response.status_code), json.dumps(shown, ensure_ascii=False)


def grpc_call(target: str, case: str) -> tuple[str, str, str]:
    with grpc.insecure_channel(target) as channel:
        try:
            channel.unary_unary(f"/{SERVICE}/Pay")(case.encode(), timeout=5)
            return "OK", "", ""
        except grpc.RpcError as error:
            trailers = {m.key: m.value for m in (error.trailing_metadata() or ())}
            code = trailers.get("x-error-code", "")
            return error.code().name, error.details() or "", code


def main() -> None:
    http_port, grpc_port = free_port(), free_port()
    proc = subprocess.Popen([sys.executable, "service.py", str(http_port), str(grpc_port)], env=os.environ)
    base, target = f"http://127.0.0.1:{http_port}", f"127.0.0.1:{grpc_port}"
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            httpx.get(f"{base}/system/health/readyz", timeout=1)
            break
        except httpx.HTTPError:
            time.sleep(0.2)
    log(f"servicewright {version('servicewright')}, grpcio {version('grpcio')}")
    try:
        log("--- one use case, two transports")
        log(f"    {'case':<12} {'HTTP':<50} gRPC")
        for case in CASES:
            status, body = http_call(base, case)
            code, details, error_code = grpc_call(target, case)
            http_column = f"{status} {body}"
            grpc_column = f"{code}" + (f": {details}" if details else "") + (f"  [x-error-code={error_code}]" if error_code else "")
            log(f"    {case:<12} {http_column:<50} {grpc_column}")
    finally:
        proc.terminate()
        proc.wait(timeout=20)


if __name__ == "__main__":
    main()
