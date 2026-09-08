"""What each library costs to install and to import, with and without its extras.

For every package below: a fresh virtual environment, an install of the bare package, a count of
the distributions that came with it, the wheels' total size, and the time to import the package
root. Then the same with one extra, so the difference is the extra's price. Finally, what a
missing extra says when you reach for the thing it provides.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

MISSING_EXTRA = [
    ("clientwright", "import clientwright.adapters.httpx"),
    ("servicewright", "import servicewright.adapters.fastapi"),
    ("redis-client-kit", "import redis_client_kit.settings"),
    ("grpc-client-kit", "from grpc_client_kit.interceptors.deadline import AsyncDeadlineBudgetInterceptor; "
                        "print('imported; HAS_DEADLINE_BUDGET =', __import__('grpc_client_kit.interceptors.deadline', "
                        "fromlist=['x']).HAS_DEADLINE_BUDGET)"),
]

PACKAGES = [
    ("deadline-budget", "deadline_budget", None),
    ("clientwright", "clientwright", None),
    ("grpc-client-kit", "grpc_client_kit", "deadline"),
    ("redis-client-kit", "redis_client_kit", "settings"),
    ("servicewright", "servicewright", "fastapi"),
    ("sqlalchemy-foundation-kit", "sqlalchemy_foundation_kit", "metrics"),
    ("aiokafka-foundation-kit", "aiokafka_foundation_kit", "models"),
    ("pg-partsmith", "pg_partsmith", "cli"),
]
IMPORT_RUNS = 5


def log(msg: str) -> None:
    print(msg, flush=True)


def measure(venv: Path, package: str, module: str) -> tuple[int, float, float]:
    """Distributions installed, megabytes on disk, and the best of five import times in ms."""
    python = venv / "bin" / "python"
    count = int(
        subprocess.run(
            [python, "-c", "from importlib.metadata import distributions; print(len(list(distributions())))"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    )
    site = next((venv / "lib").glob("python*/site-packages"))
    size = sum(f.stat().st_size for f in site.rglob("*") if f.is_file()) / 1024 / 1024
    best = min(
        float(
            subprocess.run(
                [python, "-X", "importtime", "-c", f"import {module}"], capture_output=True, text=True
            ).stderr.strip().splitlines()[-1].split("|")[1].strip()
        )
        / 1000
        for _ in range(IMPORT_RUNS)
    )
    return count, size, best


def install(venv: Path, spec: str) -> None:
    subprocess.run(
        ["uv", "pip", "install", "-q", "--refresh", "--python", str(venv / "bin" / "python"), spec],
        check=True, capture_output=True,
    )


def main() -> None:
    log(f"{'package':<26} {'deps':>5} {'MB':>7} {'import ms':>10}   with the extra")
    for package, module, extra in PACKAGES:
        with tempfile.TemporaryDirectory() as tmp:
            venv = Path(tmp) / "venv"
            subprocess.run(["uv", "venv", "--python", "3.13", "-q", str(venv)], check=True, capture_output=True)
            base_dists = int(
                subprocess.run(
                    [venv / "bin" / "python", "-c",
                     "from importlib.metadata import distributions; print(len(list(distributions())))"],
                    capture_output=True, text=True, check=True,
                ).stdout.strip()
            )
            install(venv, package)
            count, size, import_ms = measure(venv, package, module)
            line = f"{package:<26} {count - base_dists:>5} {size:>7.1f} {import_ms:>10.1f}"
            if extra:
                install(venv, f"{package}[{extra}]")
                count2, size2, import2 = measure(venv, package, module)
                line += (f"   [{extra}]: +{count2 - count} deps, +{size2 - size:.1f} MB, "
                         f"import {import2:.1f} ms")
            log(line)


def missing_extras() -> None:
    log("")
    log("--- reaching for what an extra provides, without the extra")
    for package, snippet in MISSING_EXTRA:
        with tempfile.TemporaryDirectory() as tmp:
            venv = Path(tmp) / "venv"
            subprocess.run(["uv", "venv", "--python", "3.13", "-q", str(venv)], check=True, capture_output=True)
            install(venv, package)
            done = subprocess.run(
                [venv / "bin" / "python", "-c", snippet], capture_output=True, text=True
            )
            if done.returncode == 0:
                log(f"    {package:<20} {done.stdout.strip() or 'no error'}")
            else:
                last = done.stderr.strip().splitlines()[-1]
                log(f"    {package:<20} {last[:150]}")


if __name__ == "__main__":
    main()
    missing_extras()
