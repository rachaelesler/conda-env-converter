# conda-env-converter

A very very basic CLI and Python package for converting a Conda
`environment.yml` file to a `conda create` command.

## Usage

### Installation

This package is not on PyPi (yet)!

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
