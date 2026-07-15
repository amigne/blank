"""Convert the application SemVer to the internal PEP 440 project version."""

import re

_PEP440_PRERELEASE = re.compile(
    r"^(alpha|beta|rc)\.(0|[1-9]\d*)$"
)

_PEP440_LOCAL_SEGMENT = re.compile(r"^[a-zA-Z0-9]+$")

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
    # PEP 440 in its original form. Encode as a local version segment so the
    # information is preserved (e.g. "1.0.0-my-feature" → "1.0.0+my.feature").
    local = prerelease.replace("-", ".")
    for segment in local.split("."):
        if not _PEP440_LOCAL_SEGMENT.fullmatch(segment):
            raise ValueError(
                f"Cannot convert pre-release tag {prerelease!r} to a PEP 440 "
                f"local version: segment {segment!r} is not alphanumeric"
            )
    return f"{base_version}+{local}"