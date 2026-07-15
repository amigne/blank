"""Convert the application SemVer to the internal PEP 440 project version."""

import re

_PEP440_PRERELEASE = re.compile(
    r"^(alpha|beta|rc)\.(0|[1-9]\d*)$"
)

_PEP440_PRERELEASE_PREFIX = {
    "alpha": "a",
    "beta": "b",
    "rc": "rc",
}

def to_package_version(app_version: str) -> str:
    """Return a PEP 440 version suitable for uv project metadata."""
    base_version, separator, prerelease = app_version.partition("-")

    if not separator:
        return base_version

    match = _PEP440_PRERELEASE.fullmatch(prerelease)
    if match is not None:
        name, number = match.groups()
        return f"{base_version}{_PEP440_PRERELEASE_PREFIX[name]}{number}"

    # Free-form pre-release tag: valid for the application and Docker, but not
    # PEP 440 in its original form.
    return f"{base_version}.dev0"