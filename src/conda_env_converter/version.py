"""Versioning functionality.

Robust error handling is used in this file so that we get useful log
messages if versioning fails.
"""

# pyright: strict

import logging
import subprocess
from pathlib import Path

GIT_DESCRIBE_COMMAND = "git describe --tags --dirty"
VERSION_FILENAME = "VERSION"
VERSION_FILEPATH = Path(VERSION_FILENAME)
FALLBACK_VERSION = "unknown"


def get_git_describe_version() -> str | None:
    """Return the version from `git describe`, or None if not available."""
    try:
        return (
            subprocess.check_output(GIT_DESCRIBE_COMMAND.split(" "))
            .decode("ascii")
            .strip()
        )
    # Robust error handling so we get useful log messages
    except subprocess.CalledProcessError as exc:
        print(f"WARNING: Git describe command failed with exception: {exc}")
    except (FileNotFoundError, OSError) as exc:
        print(f"WARNING: Git not available: {exc}")
    except subprocess.TimeoutExpired as exc:
        print(f"WARNING: Git describe timed out: {exc}")
    # Okay to catch bare Exception here to allow versioning to work
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: git error: {exc}")
    return None


def get_version_from_file(filepath: Path = VERSION_FILENAME) -> str | None:
    """Return version string from a file (or None if unavailable).

    Args:
        filepath: Path to the version file

    Returns:
        Version string from file, or None if not available

    """
    if not filepath.exists():
        print(f"WARNING: Version file not found: {filepath}")
        return None
    if not filepath.is_file():
        print(f"WARNING: Path exists but is not a file: {filepath}")
        return None
    with open(filepath, "r") as f:
        version = f.readline().strip()
    if not version:
        print(f"WARNING: Version file is empty: {filepath}")
        return None
    return version


def get_tool_version(version_file: Path = VERSION_FILEPATH) -> str:
    """Return the version of this tool.

    Attempts to retrieve the version from `git describe` if available,
    otherwise retrieves the version from a VERSION file. If neither
    of these sources are available, returns a fallback version.
    """
    # Try and retrieve version from git describe
    git_version = get_git_describe_version()
    if git_version:
        return git_version

    # Version from git describe not available, try and retrieve
    # from file
    version_from_file = get_version_from_file(version_file)
    if version_from_file:
        return version_from_file

    # Version from file not available, return fallback version
    return FALLBACK_VERSION


def write_version_file(
    version_file: str = VERSION_FILENAME, *, fail_silently: bool = False
) -> None:
    """Calculate the application version and write it to file.

    Args:
        version_file:
            Path to file to which the version should be written.
            Defaults to VERSION_FILENAME.
        fail_silently:
            If True, suppresses exceptions. If False, exceptions are
            raised. Defaults to False (exceptions will be raised).

    """
    try:
        version = get_tool_version(Path(version_file))
        with open(version_file, "w") as f:
            f.write(version)
        logging.info(f"Version ({version}) written to file: {version_file}")
    except Exception as exc:
        if fail_silently:
            logging.error(f"Unable to write version file. {exc}")
            return
        raise (exc)
