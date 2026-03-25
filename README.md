# Minimal Python template

Template for a minimal Python 3 tool/package that can be installed and
packaged with [setuptools](https://setuptools.pypa.io/en/latest/).

## Template Usage Instructions

TODO (usr) This section and its header can be removed once the instructions have
been followed.

Follow the following steps:

* Create a new template repository from this repository.
* Rename the `src/minimal_python_template` directory with your python package
name

  ```bash
  mv src/minimal_python_template src/$PROJECT_NAME
  ```

  * Place your own package source code in this directory
* Replace "minimal_python_template" and "minimal-python-template" in all files
with your python tool/package name.

  ```bash
  # Update the below lines with your project name
  PROJECT_NAME=my_cool_project
  PROJECT_NAME_HYPHENATED=my-cool-project

  find . -not -path "./.git/*" -type f \
    -exec sed -i "s/minimal_python_template/$PROJECT_NAME/g" {} +

  find . -not -path "./.git/*" -type f \
    -exec sed -i "s/minimal-python-template/$PROJECT_NAME_HYPHENATED/g" {} +
  ```

* Grep project files for "TODO (usr)" and follow instructions for customising
the template

  ```bash
  grep -R "TODO (usr)" ./
  ```

## Installation

### Installation requirements

* pip (tested with pip v25.2)

### Installation instructions

Create and activate a virtual environment, then run:

```bash
pip install .
```

## Usage

```bash
minimal_python_template
```

## Creating a tarball/wheel

Activate your virtual environment, install the Python
[`build`](https://build.pypa.io/en/stable/) package, move to the base of this
directory, then run:

```bash
python -m build
```
