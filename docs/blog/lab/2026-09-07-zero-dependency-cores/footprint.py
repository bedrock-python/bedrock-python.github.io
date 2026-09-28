"""Verify bare installs and extras in clean environments; optionally measure imports."""

import argparse
import json
import os
import platform
import statistics
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = (
    ("deadline_budget", (("deadline-budget-core", "deadline-budget==0.1.3"),)),
    (
        "clientwright",
        (
            ("clientwright-core", "clientwright==0.5.0"),
            ("clientwright-httpx", "clientwright[httpx]==0.5.0"),
            ("clientwright-httpx-deadline", "clientwright[httpx,deadline]==0.5.0"),
        ),
    ),
    (
        "servicewright",
        (
            ("servicewright-core", "servicewright==0.13.1"),
            ("servicewright-fastapi", "servicewright[fastapi]==0.13.1"),
        ),
    ),
)
INVENTORY = """
import json, sys, sysconfig
from importlib.metadata import distributions
from pathlib import Path
site = Path(sysconfig.get_path('purelib'))
print(json.dumps({
    'python': sys.version,
    'packages': {d.metadata['Name']: d.version for d in distributions()},
    'site_mib': sum(p.stat().st_size for p in site.rglob('*') if p.is_file()) / 2**20,
}))
"""
IMPORT = """
import importlib, sys, time
start = time.perf_counter()
importlib.import_module(sys.argv[1])
print((time.perf_counter() - start) * 1000)
"""


def run(*args):
    result = subprocess.run(
        [str(arg) for arg in args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=300,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--measure", action="store_true", help="Five fresh-process imports per case"
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Write inventories and optional measurements as JSON",
    )
    args = parser.parse_args()
    report = {
        "measured_at_utc": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "cases": [],
    }
    for module, stages in CASES:
        with tempfile.TemporaryDirectory(prefix="bedrock-optional-") as temporary:
            environment = Path(temporary) / "venv"
            run("uv", "venv", "--python", "3.13", "--no-project", environment)
            python = environment / (
                "Scripts/python.exe" if os.name == "nt" else "bin/python"
            )
            for case, spec in stages:
                print(f"Installing {spec} in an isolated environment...", flush=True)
                run(
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    python,
                    "--constraint",
                    ROOT / "constraints.txt",
                    spec,
                )
                bootstrap = (
                    "import runpy, sys; "
                    f"sys.path.insert(0, {str(ROOT)!r}); "
                    f"sys.argv = ['probe.py', {case!r}]; "
                    f"runpy.run_path({str(ROOT / 'probe.py')!r}, run_name='__main__')"
                )
                print(run(python, "-I", "-B", "-c", bootstrap), flush=True)
                inventory = json.loads(run(python, "-I", "-B", "-c", INVENTORY))
                row = {"case": case, "installed": spec, **inventory}
                if args.measure:
                    samples = [
                        float(run(python, "-I", "-B", "-c", IMPORT, module))
                        for _ in range(5)
                    ]
                    row["import_samples_ms"] = samples
                    row["import_median_ms"] = statistics.median(samples)
                report["cases"].append(row)
                print(
                    f"{case}: {len(row['packages'])} distributions, {row['site_mib']:.2f} MiB",
                    flush=True,
                )
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Report: {args.report}", flush=True)
    print("PASS: all isolated-install scenarios", flush=True)


if __name__ == "__main__":
    main()
