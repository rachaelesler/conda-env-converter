# conda-env-converter

CLI and Python package for converting a Conda `environment.yml` file to a
`conda create` command that can be run on the command line.

## Usage

### Installation

Install the latest version with:

```bash
pip install git+ssh://git@github.com/rachaelesler/conda-env-converter.git
```

Install a specific version with:

```bash
RELEASE_VERSION="2026.03.4"
pip install git+ssh://git@github.com/rachaelesler/conda-env-converter.git@${RELEASE_VERSION}
```

### Running

```bash
conda_env_converter --help
```

## Developer quickstart

### Developing with a Conda environment

Requires Conda ([miniforge](https://conda-forge.org/download/) is
recommended).

Clone this repository, `cd` into the repo's directory and run the following:

```bash
# Create and activate development Conda environment for this repo
conda env create --name conda_env_converter --file environment.yml
conda activate conda_env_converter
# Install in editable mode
pip install -e .
```

## Creating a tarball/wheel

Activate a virtual environment (i.e., activate a Conda environment or a
`virtualenv` environment), install the Python
[`build`](https://build.pypa.io/en/stable/) package, move to the base of this
directory, then run:

```bash
python -m build
```
