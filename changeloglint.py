from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


UNRELEASED_HEADING_RE = re.compile(r"^##\s*\[Unreleased\]\s*$", re.IGNORECASE)
VERSION_HEADING_RE = re.compile(r"^##\s*\[([^\]]+)\]\s*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
LOCAL_LINK_RE = re.compile(r"^[^.]*://|^#|^mailto:", re.IGNORECASE)


@dataclass(frozen=True)
class Issue:
    path: str
    line: int
    message: str
    kind: str


@dataclass
class ChangelogReport:
    issues: List[Issue] = field(default_factory=list)

    def add(self, path: str, line: int, message: str, kind: str) -> None:
        self.issues.append(Issue(path=path, line=line, message=message, kind=kind))


def _normalize_issue_type(kind: str) -> str:
    return kind.strip().lower().replace(" ", "_") or "issue"


def _validate_version_heading(text: str) -> Optional[str]:
    match = VERSION_HEADING_RE.match(text.strip())
    if not match:
        return None
    return match.group(1)


def lint_changelog(path: str) -> ChangelogReport:
    report = ChangelogReport()
    if not Path(path).is_file():
        report.add(path, 0, "missing changelog file", "missing")
        return report

    lines: List[str] = []
    with open(path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    if not lines:
        report.add(path, 0, "empty changelog file", "empty")
        return report

    heading_types: List[str] = []
    unreleased_indices: List[int] = []
    version_indices: List[tuple[int, str]] = []

    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if UNRELEASED_HEADING_RE.match(stripped):
            unreleased_indices.append(index)
            heading_types.append("unreleased")
        else:
            version = _validate_version_heading(stripped)
            if version is not None:
                version_indices.append((index, version))
                heading_types.append("version")

    if not unreleased_indices:
        report.add(path, 1, "missing [Unreleased] heading", "missing_unreleased")
    if len(unreleased_indices) > 1:
        report.add(
            path,
            unreleased_indices[1],
            "duplicate [Unreleased] heading",
            "duplicate_unreleased",
        )
    if len(version_indices) > 1:
        seen: List[str] = []
        for line_no, version in version_indices:
            normalized = version.strip().lower()
            if normalized in seen:
                report.add(
                    path,
                    line_no,
                    f"duplicate version heading: {version}",
                    "duplicate_version",
                )
            seen.append(normalized)

    for index, line in enumerate(lines, start=1):
        for link in LINK_RE.findall(line):
            if LOCAL_LINK_RE.match(link):
                continue
            target = link.lstrip("./")
            target_path = Path(path).with_name(target)
            if not target_path.exists():
                report.add(
                    path,
                    index,
                    f"broken local changelog link: {link}",
                    "broken_link",
                )

    return report


def _render_text(report: ChangelogReport) -> str:
    if not report.issues:
        return "changeloglint: ok"
    lines = [f"changeloglint: {len(report.issues)} issue(s)"]
    for issue in report.issues:
        location = f"{issue.path}:{issue.line}" if issue.line else issue.path
        lines.append(f"  {issue.kind} -> {location}: {issue.message}")
    return "\n".join(lines)


def _render_json(report: ChangelogReport) -> str:
    payload = [
        {
            "path": issue.path,
            "line": issue.line,
            "kind": issue.kind,
            "message": issue.message,
        }
        for issue in report.issues
    ]
    return json.dumps({"issues": payload}, indent=2)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="changeloglint",
        description="Lint changelog fragments for common issues.",
    )
    parser.add_argument("path", help="path to a CHANGELOG markdown file")
    parser.add_argument("--json", action="store_true", help="emit JSON report")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return 0
        raise

    report = lint_changelog(args.path)
    if args.json:
        print(_render_json(report))
    else:
        print(_render_text(report))
    return 0 if not report.issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
