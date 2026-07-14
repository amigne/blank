"""Synchronize pyproject.toml version from the root VERSION file."""

import argparse
import re
import sys

from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
PYPROJECT_FILE = BACKEND_DIR / "pyproject.toml"

sys.path.insert(0, str(BACKEND_DIR))

from app.version import APP_VERSION  # noqa: E402
from app.package_version import to_package_version  # noqa: E402


PROJECT_VERSION_LINE = re.compile(
    r'^version\s*=\s*"[^"]*"\s*$',
    flags=re.MULTILINE,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()

    current_content = PYPROJECT_FILE.read_text(encoding="utf-8")
    expected_version = to_package_version(APP_VERSION)

    expected_content, replacements = PROJECT_VERSION_LINE.subn(
        f'version = "{expected_version}"',
        current_content,
        count=1,
    )

    if replacements != 1:
        raise RuntimeError(
            f"Expected exactly one top-level version in {PYPROJECT_FILE}"
        )

    if arguments.check:
        if current_content != expected_content:
            raise SystemExit(
                f"{PYPROJECT_FILE} is not synchronized with VERSION. "
                "Run: python scripts/sync_package_version.py"
            )
        return

    if current_content != expected_content:
        PYPROJECT_FILE.write_text(expected_content, encoding="utf-8")


if __name__ == "__main__":
    main()