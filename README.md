# conda-env-converter

CLI and Python package for converting a Conda `environment.yml` file to a
`conda create` command that can be run on the command line.

## Installation

### Installation requirements

* Conda package manager ([miniforge](https://conda-forge.org/download/) is
recommended)

There are no other dependencies.

### Install with pip

After cloning this repository, move into the directory and run:

```bash
pip install -e .
```

## Usage

```bash
conda_env_converter --help
```

## Creating a tarball/wheel

Activate a virtual environment (i.e., activate a Conda environment or a
`virtualenv` environment), install the Python
[`build`](https://build.pypa.io/en/stable/) package, move to the base of this
directory, then run:

```bash
python -m build
```
