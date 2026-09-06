"""Run the suite once per history variant and print which test caught which bug."""

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

VARIANTS = ["clean", "enum_leftover", "wrong_name_in_downgrade", "drift", "two_heads", "bad_name"]
FILES = sys.argv[1:] or ["tests/test_plain_ci.py", "tests/test_by_hand.py", "tests/test_gauntlet.py"]
MARK = {"passed": "pass", "failed": "FAIL", "error": "ERROR", "skipped": "skip"}


def run(variant: str) -> dict[str, str]:
    report = Path(f".matrix-{variant}.xml")
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={report}", *FILES],
        env={**os.environ, "VARIANT": variant},
        capture_output=True,
    )
    outcome: dict[str, str] = {}
    for case in ET.parse(report).getroot().iter("testcase"):
        status = "passed"
        for child in case:
            if child.tag in ("failure", "error", "skipped"):
                status = "error" if child.tag == "error" else child.tag.replace("failure", "failed")
        outcome[case.get("name")] = status
    report.unlink()
    return outcome


results = {variant: run(variant) for variant in VARIANTS}
tests = list(results["clean"])
width = max(len(t) for t in tests)
print(f"{'':<{width}}  " + "  ".join(f"{v:^23}" for v in VARIANTS))
for test in tests:
    print(f"{test:<{width}}  " + "  ".join(f"{MARK[results[v].get(test, 'error')]:^23}" for v in VARIANTS))
