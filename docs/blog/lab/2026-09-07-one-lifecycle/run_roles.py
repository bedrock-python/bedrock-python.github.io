"""Run the same service as three deployments and print each one's lifecycle."""

import os
import signal
import socket
import subprocess
import sys
import time

import httpx


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


for role in ("all", "api", "worker"):
    port = free_port()
    proc = subprocess.Popen([sys.executable, "one_lifecycle.py", role], env={**os.environ, "PORT": str(port)},
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    lines: list[str] = []
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        line = proc.stdout.readline()
        if not line:
            break
        lines.append(line.rstrip())
        if "post_start hook" in line:
            break
    if role != "worker":
        for _ in range(3):
            httpx.get(f"http://127.0.0.1:{port}/work", timeout=2.0)
            time.sleep(0.2)
    else:
        time.sleep(0.9)
    os.kill(proc.pid, signal.SIGTERM)
    rest, _ = proc.communicate(timeout=20)
    lines += [l for l in rest.splitlines() if l.strip()]
    print(f"--- role={role} ---")
    for l in lines:
        print("  " + l)
    print(f"  exit code {proc.returncode}\n")
