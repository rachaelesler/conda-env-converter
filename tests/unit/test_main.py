"""Unit tests for conda_env_converter.__main__."""

import re

import pytest
import yaml

from conda_env_converter.__main__ import (
    CondaEnvironmentDefinition,
    InvalidEnvironmentError,
    NotAnEnvironmentFileError,
    build_conda_create_command,
    wrap_string_in_quotes,
)


def bash_command_strings_are_equal(s1: str, s2: str) -> bool:
    """Return True if two strings represent same bash command.

    Ignores newlines, extra whitespace, and backslash line conventions.
    """

    def normalise(s: str) -> str:
        s = s.replace("\\\n", " ")
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    return normalise(s1) == normalise(s2)


class TestGetCondaAndPipDependencies:
    """Test _get_conda_and_pip_dependencies function."""

    def test_only_conda_deps(self):
        """Test with only conda dependencies."""
        deps = ["python=3.9", "numpy", "pandas"]
        conda_deps, pip_deps = (
            CondaEnvironmentDefinition._get_conda_and_pip_dependencies(deps)
        )
        assert conda_deps == ["python=3.9", "numpy", "pandas"]
        assert pip_deps == []

    def test_only_pip_deps(self):
        """Test with only pip dependencies."""
        deps = [{"pip": ["requests", "flask"]}]
        conda_deps, pip_deps = (
            CondaEnvironmentDefinition._get_conda_and_pip_dependencies(deps)
        )
        assert conda_deps == []
        assert pip_deps == ["requests", "flask"]

    def test_mixed_deps(self):
        """Test with mixed conda and pip dependencies."""
        deps = ["python=3.9", {"pip": ["requests"]}, "numpy"]
        conda_deps, pip_deps = (
            CondaEnvironmentDefinition._get_conda_and_pip_dependencies(deps)
        )
        assert conda_deps == ["python=3.9", "numpy"]
        assert pip_deps == ["requests"]

    def test_unrecognised_dep(self, capsys):
        """Test with unrecognised dependency format."""
        deps = ["python=3.9", {"unknown": "value"}]
        conda_deps, pip_deps = (
            CondaEnvironmentDefinition._get_conda_and_pip_dependencies(deps)
        )
        assert conda_deps == ["python=3.9"]
        assert pip_deps == []
        captured = capsys.readouterr()
        assert "Warning: skipping unrecognised dependency entry" in captured.err

    def test_empty_deps(self):
        """Test with empty dependencies."""
        deps = []
        conda_deps, pip_deps = (
            CondaEnvironmentDefinition._get_conda_and_pip_dependencies(deps)
        )
        assert conda_deps == []
        assert pip_deps == []


class TestWrapStringInQuotes:
    """Test wrap_string_in_quotes function."""

    def test_no_special_chars(self):
        """Test string without special characters."""
        assert wrap_string_in_quotes("python") == "python"

    def test_with_space(self):
        """Test string with space."""
        assert wrap_string_in_quotes("python=3.9") == '"python=3.9"'

    def test_with_greater_than(self):
        """Test string with >."""
        assert wrap_string_in_quotes("python>3.8") == '"python>3.8"'

    def test_with_less_than(self):
        """Test string with <."""
        assert wrap_string_in_quotes("python<3.10") == '"python<3.10"'

    def test_with_equals(self):
        """Test string with =."""
        assert wrap_string_in_quotes("python=3.9") == '"python=3.9"'

    def test_multiple_special(self):
        """Test string with multiple special characters."""
        assert wrap_string_in_quotes("python>=3.8,<3.10") == '"python>=3.8,<3.10"'


class TestCondaEnvironmentDefinition:
    """Test CondaEnvironmentDefinition class."""

    def test_from_environment_yml_valid(self, tmp_path):
        """Test from_environment_yml with valid file."""
        env_data = {
            "name": "test_env",
            "channels": ["conda-forge", "defaults"],
            "prefix": "/path/to/env",
            "dependencies": ["python=3.9", {"pip": ["requests"]}],
        }
        path = tmp_path / "env.yml"
        with open(path, "w") as f:
            yaml.dump(env_data, f)

        env_def = CondaEnvironmentDefinition.from_environment_yml(path)
        assert env_def.name == "test_env"
        assert env_def.channels == ["conda-forge", "defaults"]
        assert env_def.prefix == "/path/to/env"
        assert env_def.conda_dependencies == ["python=3.9"]
        assert env_def.pip_dependencies == ["requests"]

    def test_from_environment_yml_not_dict(self, tmp_path):
        """Test from_environment_yml with non-dict content."""
        path = tmp_path / "env.yml"
        with open(path, "w") as f:
            f.write("not a dict\n")

        with pytest.raises(NotAnEnvironmentFileError):
            CondaEnvironmentDefinition.from_environment_yml(path)

    def test_from_environment_yml_missing_keys(self, tmp_path):
        """Test from_environment_yml with missing required keys."""
        env_data = {"name": "test_env"}  # missing channels and dependencies
        path = tmp_path / "env.yml"
        with open(path, "w") as f:
            yaml.dump(env_data, f)

        with pytest.raises(KeyError):
            CondaEnvironmentDefinition.from_environment_yml(path)


class TestBuildCondaCreateCommand:
    """Test build_conda_create_command function."""

    def test_basic_command(self, capsys):
        """Test basic conda create command."""
        env_def = CondaEnvironmentDefinition(
            name="test_env",
            channels=["conda-forge"],
            prefix=None,
            conda_dependencies=["python=3.9", "numpy"],
            pip_dependencies=[],
        )
        command = build_conda_create_command(
            env_def, env_name=None, no_default_packages=False, use_channels=False
        )
        assert command == 'conda create --name test_env "python=3.9" numpy'
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_with_env_name_override(self):
        """Test with environment name override."""
        env_def = CondaEnvironmentDefinition(
            name="original_env",
            channels=[],
            prefix=None,
            conda_dependencies=["foo"],
            pip_dependencies=[],
        )
        command = build_conda_create_command(
            env_def, env_name="new_env", no_default_packages=False, use_channels=False
        )
        assert command == "conda create --name new_env foo"

    def test_no_env_name(self):
        """Test with no environment name."""
        env_def = CondaEnvironmentDefinition(
            name="",
            channels=[],
            prefix=None,
            conda_dependencies=["python"],
            pip_dependencies=[],
        )
        with pytest.raises(InvalidEnvironmentError):
            build_conda_create_command(
                env_def, env_name=None, no_default_packages=False, use_channels=False
            )

    def test_no_default_packages(self):
        """Test with --no-default-packages."""
        env_def = CondaEnvironmentDefinition(
            name="test_env",
            channels=[],
            prefix=None,
            conda_dependencies=["python"],
            pip_dependencies=[],
        )
        command = build_conda_create_command(
            env_def, env_name=None, no_default_packages=True, use_channels=False
        )
        expected = "conda create --name test_env --no-default-packages python"
        assert bash_command_strings_are_equal(command, expected)

    def test_use_channels(self):
        """Test with --channels."""
        env_def = CondaEnvironmentDefinition(
            name="test_env",
            channels=["conda-forge", "defaults"],
            prefix=None,
            conda_dependencies=["bar"],
            pip_dependencies=[],
        )
        command = build_conda_create_command(
            env_def, env_name=None, no_default_packages=False, use_channels=True
        )
        expected = (
            "conda create --name test_env --channel conda-forge --channel defaults bar"
        )
        assert bash_command_strings_are_equal(command, expected)

    def test_with_pip_deps(self, capsys):
        """Test with pip dependencies (should print note)."""
        env_def = CondaEnvironmentDefinition(
            name="test_env",
            channels=[],
            prefix=None,
            conda_dependencies=["python"],
            pip_dependencies=["requests", "flask"],
        )
        command = build_conda_create_command(
            env_def, env_name=None, no_default_packages=False, use_channels=False
        )
        expected = "conda create --name test_env python"
        assert bash_command_strings_are_equal(command, expected)
        captured = capsys.readouterr()
        assert "pip dependencies cannot be expressed" in captured.out
        assert "requests" in captured.out
        assert "flask" in captured.out

    def test_dep_with_dash(self):
        """Test dependency with leading dash."""
        env_def = CondaEnvironmentDefinition(
            name="test_env",
            channels=[],
            prefix=None,
            conda_dependencies=["- python=3.9"],
            pip_dependencies=[],
        )
        command = build_conda_create_command(
            env_def, env_name=None, no_default_packages=False, use_channels=False
        )
        expected = 'conda create --name test_env "python=3.9"'
        assert bash_command_strings_are_equal(command, expected)

    def test_empty_dep(self):
        """Test empty dependency."""
        env_def = CondaEnvironmentDefinition(
            name="test_env",
            channels=[],
            prefix=None,
            conda_dependencies=["", "python"],
            pip_dependencies=[],
        )
        command = build_conda_create_command(
            env_def, env_name=None, no_default_packages=False, use_channels=False
        )
        expected = "conda create --name test_env python"
        assert bash_command_strings_are_equal(command, expected)
