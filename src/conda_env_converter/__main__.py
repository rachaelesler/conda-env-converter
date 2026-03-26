"""Main entrypoint."""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from conda_env_converter import __version__


class NotAnEnvironmentFileError(Exception):
    """Raised when a file provided is not a Conda environment.yml file."""

    pass


class InvalidEnvironmentError(Exception):
    """Raised when the Conda environment is invalid in some way."""

    pass


@dataclass
class CondaEnvironmentDefinition:
    """Encapsulates the data from a Conda environment.yml file."""

    name: str
    channels: list[str] | None
    prefix: str | None
    conda_dependencies: list[str]
    pip_dependencies: list[str]

    @classmethod
    def from_environment_yml(cls, path: Path) -> "CondaEnvironmentDefinition":
        """Initialise object from environment.yml file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise NotAnEnvironmentFileError(
                f"Error: {path} does not appear to be a valid environment.yml file."
            )
        conda_dependencies, pip_dependencies = cls._get_conda_and_pip_dependencies(
            data["dependencies"]
        )
        return cls(
            name=data["name"],
            channels=data.get("channels"),
            prefix=data.get("prefix"),
            conda_dependencies=conda_dependencies,
            pip_dependencies=pip_dependencies,
        )

    @staticmethod
    def _get_conda_and_pip_dependencies(
        dependencies: list,
    ) -> tuple[list[str], list[str]]:
        """Separate conda dependencies from pip dependencies.

        Returns a tuple where the first item is a list of the Conda
        dependencies and the second item is a list of the pip dependencies.
        """
        conda_dependencies: list[str] = []
        pip_dependencies: list[str] = []

        for dep in dependencies:
            if isinstance(dep, str):
                conda_dependencies.append(dep)
            elif isinstance(dep, dict) and "pip" in dep:
                pip_dependencies.extend(dep["pip"])
            else:
                print(
                    f"Warning: skipping unrecognised dependency entry: {dep!r}",
                    file=sys.stderr,
                )

        return (conda_dependencies, pip_dependencies)


def wrap_string_in_quotes(s: str) -> str:
    """Wrap a string in quotes if it contains shell-special characters."""
    if any(c in s for c in "><= "):
        return f'"{s}"'
    return s


def build_conda_create_command(
    environment_definition: CondaEnvironmentDefinition,
    env_name: str | None,
    *,
    no_default_packages: bool,
    use_channels: bool,
) -> str:
    """Return `conda create` command from environment dict.

    Args:
        environment_definition:
            Conda environment definition.
        env_name:
            Name of environment. If not provided, uses the environment
            name from the `env` arg.
        no_default_packages: If True, appends the
            `--no-default-packages` argument to the `conda create`
            command.
        use_channels: If True, add `--channels` argument(s) based on
            the channels in `env`.

    Returns:
        The `conda create` command.

    """
    name = env_name or environment_definition.name
    if not name:
        raise InvalidEnvironmentError(
            "No environment name found in file and none supplied via --name.",
        )

    parts = ["conda create", f"--name {wrap_string_in_quotes(name)}"]

    if no_default_packages:
        parts.append("--no-default-packages")
    if use_channels and environment_definition.channels:
        for channel in environment_definition.channels:
            parts.append(f"--channel {channel}")

    for dep in environment_definition.conda_dependencies:
        # Strip the leading "- " that some files include as plain strings
        dep_formatted = dep.strip().lstrip("- ")
        if dep_formatted:
            parts.append(wrap_string_in_quotes(dep_formatted))

    if environment_definition.pip_dependencies:
        print(
            "Note: the following pip dependencies cannot be expressed "
            "in `conda create` and must be installed separately with "
            "`pip install`:\n  " + "\n  ".join(environment_definition.pip_dependencies),
        )

    return " ".join(parts)


def main() -> None:
    """Create CLI for this tool."""
    description = "Build a `conda create` command from a Conda environment file."
    epilog = """
examples:
  %(prog)s --file environment.yml
  %(prog)s --file environment.yml --name myenv
  %(prog)s -f environment.yml --no-default-packages
        """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog,
    )
    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        help="Path to the environment.yml file.",
        required="--version" not in sys.argv,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--name",
        "-n",
        metavar="NAME",
        default=None,
        help="Override the environment name from the file.",
    )
    parser.add_argument(
        "--no-default-packages",
        action="store_true",
        default=False,
        help="Pass --no-default-packages to conda create.",
    )
    parser.add_argument(
        "--use-channels",
        action="store_true",
        default=False,
        help="Pass --channels to conda create. "
        "This will fail silently if there are no channels in the environment file.",
    )

    args = parser.parse_args()

    if not args.file.exists():
        raise FileNotFoundError(f"File not found: {args.file}")

    env = CondaEnvironmentDefinition.from_environment_yml(args.file)
    command = build_conda_create_command(
        environment_definition=env,
        env_name=args.name,
        no_default_packages=args.no_default_packages,
        use_channels=args.use_channels,
    )

    print(command)


if __name__ == "__main__":
    main()
