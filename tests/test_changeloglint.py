from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from changeloglint import lint_changelog, main


def _write(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_missing_unreleased_heading() -> None:
    path = _write(Path("/tmp/changeloglint-case1.md"), "## [1.0.0]\n- one\n")
    report = lint_changelog(path)
    assert any(issue.kind == "missing_unreleased" for issue in report.issues)


def test_valid_changelog_is_clean() -> None:
    path = _write(
        Path("/tmp/changeloglint-case2.md"), "## [Unreleased]\n- change\n\n## [1.0.0]\n- fix\n"
    )
    report = lint_changelog(path)
    assert report.issues == []


def test_empty_file_reports_empty() -> None:
    path = _write(Path("/tmp/changeloglint-case3.md"), "")
    report = lint_changelog(path)
    assert any(issue.kind == "empty" for issue in report.issues)


def test_missing_file_reports_missing() -> None:
    report = lint_changelog("/tmp/changeloglint-missing.md")
    assert any(issue.kind == "missing" for issue in report.issues)


def test_duplicate_unreleased_heading() -> None:
    text = "## [Unreleased]\n- a\n\n## [Unreleased]\n- b\n"
    path = _write(Path("/tmp/changeloglint-case4.md"), text)
    report = lint_changelog(path)
    assert any(issue.kind == "duplicate_unreleased" for issue in report.issues)


def test_duplicate_version_heading() -> None:
    text = "## [1.0.0]\n- a\n\n## [1.0.0]\n- b\n"
    path = _write(Path("/tmp/changeloglint-case5.md"), text)
    report = lint_changelog(path)
    assert any(issue.kind == "duplicate_version" for issue in report.issues)


def test_main_returns_zero_for_clean_file() -> None:
    path = _write(
        Path("/tmp/changeloglint-clean.md"), "## [Unreleased]\n- change\n\n## [1.0.0]\n- fix\n"
    )
    assert main([path]) == 0


def test_main_returns_nonzero_for_issues() -> None:
    path = _write(Path("/tmp/changeloglint-dirty.md"), "## [1.0.0]\n- one\n")
    assert main([path]) == 1


def test_main_json_output(capsys: pytest.CaptureFixture[str]) -> None:
    path = _write(Path("/tmp/changeloglint-json.md"), "## [1.0.0]\n- one\n")
    rc = main([path, "--json"])
    assert rc == 1
    output = capsys.readouterr().out
    assert "broken_link" in output or "missing_unreleased" in output


def test_help_flag_returns_zero() -> None:
    assert main(["--help"]) == 0


def test_broken_local_link_detection() -> None:
    text = "## [Unreleased]\n- [notes](missing-file.md)\n"
    path = _write(Path("/tmp/changeloglint-case6.md"), text)
    report = lint_changelog(path)
    assert any(issue.kind == "broken_link" for issue in report.issues)


def test_link_reconstruction_uses_changelog_directory() -> None:
    directory = Path("/tmp/changeloglint-dir")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "existing.md").write_text("x", encoding="utf-8")
    text = "## [Unreleased]\n- [notes](./existing.md)\n"
    path = _write(directory / "CHANGELOG.md", text)
    report = lint_changelog(path)
    assert not any(issue.kind == "broken_link" for issue in report.issues)
