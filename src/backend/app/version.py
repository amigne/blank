"""Application version loaded from the repository VERSION file."""

import re

from pathlib import Path

_NUMERIC_IDENTIFIER = r"(?:0|[1-9]\d*)"
_NON_NUMERIC_IDENTIFIER = r"(?:[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
_PRERELEASE_IDENTIFIER = (
    rf"(?:{_NUMERIC_IDENTIFIER}|{_NON_NUMERIC_IDENTIFIER})"
)

SEMVER_PATTERN = re.compile(
    rf"^"
    rf"{_NUMERIC_IDENTIFIER}\."
    rf"{_NUMERIC_IDENTIFIER}\."
    rf"{_NUMERIC_IDENTIFIER}"
    rf"(?:-{_PRERELEASE_IDENTIFIER}"
    rf"(?:\.{_PRERELEASE_IDENTIFIER})*)?"
    rf"$"
)

VERSION_FILE = Path(__file__).resolve().parents[2] / "VERSION"

def load_app_version(version_file: Path = VERSION_FILE) -> str:
    """Read and validate the application SemVer version."""
    try:
        raw_version = version_file.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise RuntimeError(
            f"Application version file is missing: {version_file}"
        ) from error
    
    version = raw_version.removesuffix("\n")
    if "\n" in version or not version:
        raise RuntimeError(
            f"Application version file must contain exactly one non-empty line: "
            f"{version_file}"
        )
    
    if not SEMVER_PATTERN.fullmatch(version):
        raise RuntimeError(
            f"Invalid application version in {version_file}: {version!r}. "
            "Expected SemVer sur as '1.2.3', '1.2.3-rc.1'. "
            "or '1.2.3-feature-x'."
        )
    
    return version

APP_VERSION = load_app_version()
