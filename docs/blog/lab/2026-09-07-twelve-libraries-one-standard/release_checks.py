"""Reject a tag/version mismatch instead of rewriting the package to fit a tag."""
import re


def require_release_tag(tag: str, package_version: str) -> None:
    match = re.fullmatch(r"(?:report-periods-)?v(\d+\.\d+\.\d+)", tag)
    if match is None or match[1] != package_version:
        raise ValueError("Release tag and package version must agree")
