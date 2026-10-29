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
# Failures are keyed by "<class or module>::<test>": some test names exist both in the gauntlet class and in handwritten files.
EXPECTED = {
    "enum_leftover": "TestMigrations::test_stairway_upgrade_downgrade",
    "wrong_name_in_downgrade": "TestMigrations::test_stairway_upgrade_downgrade",
    "head_noop_downgrade": "test_by_hand::test_every_revision_up_down_up",
    "drift": "TestMigrations::test_migrations_up_to_date",
    "two_heads": "TestMigrations::test_single_head_revision",
    "bad_name": "TestMigrations::test_naming_conventions",
    "drift_type": "TestMigrations::test_migrations_up_to_date",
    "drift_server_default": "TestMigrations::test_migrations_up_to_date",
    "drift_check_missing": "TestMigrations::test_check_constraints_match",
    "drift_enum_value": "TestMigrations::test_enum_values_match",
    "drift_index_missing": "TestMigrations::test_migrations_up_to_date",
    "drift_extra_column": "TestMigrations::test_migrations_up_to_date",
    "drift_check_expression": "test_business_rules::test_order_amount_must_be_positive[0]",
    "data_loss": "test_business_rules::test_existing_orders_survive",
}
# The gauntlet's seven checks pass on these histories: only handwritten tests catch them.
GAUNTLET_BLIND = {"head_noop_downgrade", "drift_check_expression", "data_loss"}
TIMEOUT = int(os.getenv("MATRIX_TIMEOUT", "300"))


def key(case):
    return f"{case.get('classname', '').rsplit('.', 1)[-1]}::{case.get('name')}"


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
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT,
    )
    assert completed.returncode in (0, 1), completed.stdout + completed.stderr
    cases = list(ET.parse(report).getroot().iter("testcase"))
    assert len(cases) == (3 if variant == "two_heads" else 20), completed.stdout + completed.stderr
    assert all(case.find("error") is None and case.find("skipped") is None for case in cases), completed.stdout
    failed = {key(case) for case in cases if case.find("failure") is not None}
    if variant == "clean":
        assert not failed and completed.returncode == 0, completed.stdout
    else:
        assert EXPECTED[variant] in failed and completed.returncode == 1, completed.stdout
        assert ("test_plain_ci::test_upgrade_head" in failed) == (variant == "two_heads"), completed.stdout
    if variant in GAUNTLET_BLIND:
        assert not any(name.startswith("TestMigrations::") for name in failed), completed.stdout
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
