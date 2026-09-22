"""Verify that deliberately broken histories fail for the expected reason."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

from testcontainers.community.postgres import PostgresContainer

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    "enum_leftover": "test_stairway_upgrade_downgrade",
    "wrong_name_in_downgrade": "test_stairway_upgrade_downgrade",
    "drift": "test_migrations_up_to_date",
    "two_heads": "test_single_head_revision",
    "bad_name": "test_naming_conventions",
    "drift_type": "test_migrations_up_to_date",
    "drift_server_default": "test_migrations_up_to_date",
    "drift_check_missing": "test_check_constraints_match",
    "drift_enum_value": "test_enum_values_match",
    "drift_index_missing": "test_migrations_up_to_date",
    "drift_extra_column": "test_migrations_up_to_date",
    "drift_check_expression": "test_order_amount_must_be_positive[0]",
    "data_loss": "test_existing_orders_survive",
}


def run(variant, url, directory):
    report = Path(directory) / f"{variant}.xml"
    # A branched history has no unambiguous `head`; validate that prerequisite first.
    selected = [
        "tests/test_by_hand.py::test_exactly_one_head",
        "tests/test_gauntlet.py::TestMigrations::test_single_head_revision",
        "tests/test_plain_ci.py",
    ] if variant == "two_heads" else []
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=short", "-p", "no:cacheprovider",
         f"--junitxml={report}", *selected],
        cwd=ROOT, env={**os.environ, "VARIANT": variant, "MIGRATION_TEST_URL": url},
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    assert completed.returncode in (0, 1), completed.stdout + completed.stderr
    cases = list(ET.parse(report).getroot().iter("testcase"))
    assert len(cases) == (3 if variant == "two_heads" else 20), completed.stdout + completed.stderr
    assert all(case.find("error") is None and case.find("skipped") is None for case in cases), completed.stdout
    failed = {case.get("name") for case in cases if case.find("failure") is not None}
    if variant == "clean":
        assert not failed and completed.returncode == 0, completed.stdout
    else:
        assert EXPECTED[variant] in failed and completed.returncode == 1, completed.stdout
        assert ("test_upgrade_head" in failed) == (variant == "two_heads"), completed.stdout
    if variant in {"drift_check_expression", "data_loss"}:
        assert all(case.find("failure") is None for case in cases
                   if case.get("classname", "").endswith("TestMigrations")), completed.stdout
    failures = ", ".join(sorted(failed)) or "none"
    print(f"PASS {variant}: expected failures = {failures}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variants", default=os.getenv("VARIANTS", ",".join(["clean", *EXPECTED])))
    variants = parser.parse_args().variants.split(",")
    assert set(variants) <= {"clean", *EXPECTED}, "Unknown history variant"
    with PostgresContainer("postgres:17-alpine", driver="asyncpg") as postgres, TemporaryDirectory() as directory:
        for variant in variants:
            run(variant, postgres.get_connection_url(), directory)
    print(f"PASS: {len(variants)} histories checked; no unexpected skips or setup errors")


if __name__ == "__main__":
    main()
