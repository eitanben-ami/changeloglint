# changeloglint

<p align="left">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License" />
  <img src="https://img.shields.io/badge/status-stable-green" alt="Status" />
</p>

**Lint changelog fragments for broken links, missing versions, and section issues.**

`changeloglint` is a small CLI and library that validates local CHANGELOG markdown files without network access. It catches common release-note problems before they ship: unreachable local targets, inconsistent `[Unreleased]` headings, duplicate version headings, and missing top-level `## [Unreleased]` blocks in Keep a Changelog style files.

## About

Most changelog bugs are caught too late: in CI after a release draft is published, or by users clicking a broken note link. `changeloglint` runs locally, requires no external services, and reports actionable line-level findings.

It is useful for libraries and CLIs that keep a changelog in markdown, use local relative links, and want a fast pre-commit or CI check.

## Features

- Parse Keep a Changelog markdown into versioned sections.
- Detect missing or duplicate `[Unreleased]` sections.
- Validate relative markdown links in the changelog.
- Report version formatting issues.
- CLI with readable summary output and JSON export.
- Library API for embedding in other tooling.
- Stdlib-only implementation.

## Installation

```bash
git clone https://github.com/eitanben-ami/changeloglint.git
cd changeloglint
python -m pip install -e .
```

## Usage

CLI:

```bash
changeloglint CHANGELOG.md
changeloglint CHANGELOG.md --json
```

Library:

```python
from changeloglint import lint_changelog

report = lint_changelog("CHANGELOG.md")
for issue in report.issues:
    print(issue)
```

## Project Structure

```
changeloglint/
  changeloglint.py   # parser, link checker, reporter, CLI
  pyproject.toml
  README.md
  LICENSE
  tests/
    test_changeloglint.py
```

## Tags / Keywords

changelog, markdown, lint, keep-a-changelog, release notes, link validation, cli, python
