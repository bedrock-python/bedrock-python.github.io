"""Generate, test and install a real package. Does not create repositories or publish."""
import argparse
from email.parser import BytesParser
from importlib.metadata import version
from itertools import product
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
from tempfile import mkdtemp
from textwrap import indent
import zipfile

from copier import run_copy
import yaml

from release_checks import require_release_tag

HERE = Path(__file__).resolve().parent
TEMPLATE_REF = "a1a1e7d5eafdcac08aeed7c1a0daaff31c67ac8c"
ANSWERS = {
    "project_name": "report-periods", "project_slug": "report-periods", "package_name": "report_periods",
    "project_description": "UTC month boundaries for reports", "author_name": "Example Author",
    "author_email": "author@example.com", "github_org": "example-org", "python_min_version": "3.11",
    "initial_version": "0.0.0",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", nargs="?", default="https://github.com/bedrock-python/python-library-template.git")
    parser.add_argument("--output", type=Path, help="New directory for the project, artifacts and command logs")
    args = parser.parse_args()
    output = args.output.resolve() if args.output else Path(mkdtemp(prefix="report-periods-lab-"))
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    project = output / "report-periods"
    logs = output / "logs"
    logs.mkdir()
    command_number = 0
    process_env = os.environ.copy()
    process_env.pop("VIRTUAL_ENV", None)
    process_env.pop("PYTHONPATH", None)
    process_env["UV_NO_PROGRESS"] = "1"
    process_env["PYTHONUTF8"] = "1"
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("Install uv before running this lab")

    def run(*command, cwd=None, codes=(0,), extra_env=None):
        nonlocal command_number
        command_number += 1
        result = subprocess.run(
            [str(part) for part in command], cwd=cwd or project,
            env=process_env | (extra_env or {}), capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=300,
        )
        log = logs / f"{command_number:03}.txt"
        log.write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode not in codes:
            raise RuntimeError(f"Command {command[0]} exited {result.returncode}; see {log}\n{log.read_text(encoding='utf-8')[-7000:]}")
        return result

    run_copy(args.template, project, data=ANSWERS, defaults=True, vcs_ref=TEMPLATE_REF, unsafe=True)
    run("git", "init", "-q")  # A separate repo prevents the parent's ignore rules hiding this fixture.
    run(uv, "sync", "--python", "3.13", "--group", "dev")

    def checks():
        run(uv, "run", "ruff", "check", ".")
        run(uv, "run", "ruff", "format", "--check", ".")
        run(uv, "run", "mypy", "report_periods")
        return run(uv, "run", "pytest", "--cov=report_periods", "--cov-fail-under=90")

    baseline = checks()
    assert "1 passed" in baseline.stdout, baseline.stdout
    empty_integration = run(uv, "run", "pytest", "-m", "integration", codes=(5,))
    assert "deselected" in empty_integration.stdout
    print("PASS baseline: lint, format, mypy, one version test; integration suite has no tests (exit 5)", flush=True)

    package = project / "report_periods"
    shutil.copyfile(HERE / "periods.py", package / "periods.py")
    shutil.copyfile(HERE / "test_periods.py", project / "tests/unit/test_periods.py")
    (package / "__init__.py").write_text(
        '\"\"\"UTC month boundaries for reports.\"\"\"\n\nfrom .__version__ import __version__\nfrom .periods import month_bounds\n\n__all__ = ["__version__", "month_bounds"]\n',
        encoding="utf-8",
    )
    behavior = checks()
    assert "7 passed" in behavior.stdout, behavior.stdout
    for python in ("3.11", "3.12"):
        result = run(uv, "run", "--isolated", "--python", python, "--group", "test", "pytest", "-m", "unit")
        assert "7 passed" in result.stdout, result.stdout
    print("PASS behavior: seven tests pass on Python 3.11, 3.12 and 3.13", flush=True)

    bad = package / "bad_clock.py"
    try:
        bad.write_text("from datetime import datetime\n\ndef report_time() -> datetime:\n    return datetime.now()\n", encoding="utf-8")
        lint = run(uv, "run", "ruff", "check", str(bad), "--output-format", "json", codes=(1,))
        assert "DTZ005" in {finding["code"] for finding in json.loads(lint.stdout)}
    finally:
        bad.unlink()
    source = (package / "periods.py").read_text(encoding="utf-8")
    try:
        (package / "periods.py").write_text(source.replace("year=start.year + 1", "year=start.year"), encoding="utf-8")
        failure = run(uv, "run", "pytest", "tests/unit/test_periods.py", codes=(1,))
        assert "2026-12-31" in failure.stdout and "failed" in failure.stdout, failure.stdout
    finally:
        (package / "periods.py").write_text(source, encoding="utf-8")
    print("PASS negative checks: Ruff rejects a naive clock; a wrong December boundary fails the behavior suite", flush=True)

    ci_path = project / ".github/workflows/ci.yml"
    ci = yaml.load(ci_path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    original_gate = ci["jobs"]["all-checks-passed"]["steps"][0]["run"]
    assert "contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled')" in original_gate
    assert "skipped" not in original_gate
    fixed_gate = yaml.load((HERE / "ci-gate.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader)["all-checks-passed"]
    code = fixed_gate["steps"][0]["run"]
    names = fixed_gate["needs"]
    old_false_positives = 0
    for results in product(("success", "failure", "cancelled", "skipped"), repeat=len(names)):
        jobs = {name: {"result": result} for name, result in zip(names, results, strict=True)}
        expected = 0 if all(result == "success" for result in results) else 1
        run(sys.executable, "-c", code, codes=(expected,), extra_env={"NEEDS_JSON": json.dumps(jobs)})
        old_passed = not ({"failure", "cancelled"} & set(results))
        old_false_positives += int(old_passed and expected == 1)
    run(sys.executable, "-c", code, codes=(1,), extra_env={"NEEDS_JSON": "{}"})
    assert old_false_positives == 7
    # Preserve the original workflow in the report, then install the exact demonstrated job.
    (output / "original-ci.yml").write_text(ci_path.read_text(encoding="utf-8"), encoding="utf-8")
    ci_text = ci_path.read_text(encoding="utf-8")
    updated_ci, replacements = re.subn(
        r"(?ms)^  all-checks-passed:.*?(?=^  [a-zA-Z][\w-]*:|\Z)",
        lambda _: indent((HERE / "ci-gate.yml").read_text(encoding="utf-8"), "  "), ci_text,
    )
    assert replacements == 1
    updated_jobs = yaml.load(updated_ci, Loader=yaml.BaseLoader)["jobs"]
    assert updated_jobs["all-checks-passed"] == fixed_gate
    assert {k: v for k, v in updated_jobs.items() if k != "all-checks-passed"} == {
        k: v for k, v in ci["jobs"].items() if k != "all-checks-passed"
    }
    ci_path.write_text(updated_ci, encoding="utf-8")
    print("PASS CI gate: 64 job-result combinations and missing jobs; only all-success passes", flush=True)

    # Locally model the version files from a reviewed release PR; no GitHub writes or release tag.
    (package / "__version__.py").write_text('__version__ = "0.1.0"  # x-release-please-version\n', encoding="utf-8")
    (project / ".release-please-manifest.json").write_text('{".": "0.1.0"}\n', encoding="utf-8")
    (project / "CHANGELOG.md").write_text("# Changelog\n\n## 0.1.0\n\n- Add UTC month boundaries for reports.\n", encoding="utf-8")
    for tag in ("v0.1.0", "report-periods-v0.1.0"):
        require_release_tag(tag, "0.1.0")
    for tag in ("v0.2.0", "other-v0.1.0", "v0.1.0-extra", "main"):
        try:
            require_release_tag(tag, "0.1.0")
        except ValueError:
            pass
        else:
            raise AssertionError(f"Accepted invalid release tag {tag!r}")
    checks()
    run(uv, "build", "--no-sources")
    wheels = list((project / "dist").glob("*.whl"))
    sdists = list((project / "dist").glob("*.tar.gz"))
    assert len(wheels) == len(sdists) == 1
    required = {"report_periods/__init__.py", "report_periods/__version__.py", "report_periods/periods.py", "report_periods/py.typed"}
    with zipfile.ZipFile(wheels[0]) as archive:
        assert required <= set(archive.namelist())
        metadata = BytesParser().parsebytes(archive.read("report_periods-0.1.0.dist-info/METADATA"))
        assert metadata["Name"] == "report-periods" and metadata["Version"] == "0.1.0"
        assert metadata["Requires-Python"] == ">=3.11" and metadata.get_all("Requires-Dist") is None
        wheel_code = {name: archive.read(name) for name in required}
    with tarfile.open(sdists[0]) as archive:
        for name in required:
            member = archive.extractfile(f"report_periods-0.1.0/{name}")
            assert member is not None and member.read() == wheel_code[name]
    print("PASS build: matching source/wheel modules, py.typed, metadata and six release-tag cases", flush=True)

    consumer = output / "consumer"
    consumer.mkdir()
    for label, artifact in (("wheel", wheels[0]), ("sdist", sdists[0])):
        venv = output / f"{label}-env"
        run(uv, "venv", "--python", "3.11", venv)
        interpreter = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        run(uv, "pip", "install", "--python", interpreter, "--no-deps", artifact)
        smoke = run(interpreter, "-I", HERE / "artifact_smoke.py", cwd=consumer)
        assert "PASS installed artifact" in smoke.stdout
    print("PASS installation: wheel and sdist each work in a separate clean Python 3.11 environment", flush=True)

    versions = run(uv, "run", "python", "-c", "import importlib.metadata as m, json; print(json.dumps({n: m.version(n) for n in ['ruff', 'mypy', 'pytest', 'pytest-cov']}))")
    report = {"template_ref": TEMPLATE_REF, "copier": version("copier"), "jinja2-time": version("jinja2-time"),
              "tools": json.loads(versions.stdout), "published": False, "project": str(project)}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS complete: artifacts, uv.lock, report.json and logs retained at {output}", flush=True)


if __name__ == "__main__":
    main()
