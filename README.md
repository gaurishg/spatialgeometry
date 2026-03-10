# Spatial Geometry

[![A Python Robotics Package](https://raw.githubusercontent.com/petercorke/robotics-toolbox-python/master/.github/svg/py_collection.min.svg)](https://github.com/petercorke/robotics-toolbox-python)
[![QUT Centre for Robotics Open Source](https://github.com/qcr/qcr.github.io/raw/master/misc/badge.svg)](https://qcr.github.io)

[![PyPI version](https://badge.fury.io/py/spatialgeometry.svg)](https://badge.fury.io/py/spatialgeometry)
[![Anaconda version](https://anaconda.org/conda-forge/spatialgeometry/badges/version.svg)](https://anaconda.org/conda-forge/spatialgeometry)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/spatialgeometry.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Build Status](https://github.com/jhavl/spatialgeometry/workflows/build/badge.svg?branch=main)](https://github.com/jhavl/spatialgeometry/actions?query=workflow%3Abuild)
[![codecov](https://codecov.io/gh/jhavl/spatialgeometry/branch/main/graph/badge.svg?token=YPmchbQi2v)](https://codecov.io/gh/jhavl/spatialgeometry)

<table style="border:0px">
<tr style="border:0px">
<td style="border:0px">
<img src="https://github.com/petercorke/robotics-toolbox-python/raw/master/docs/figs/RobToolBox_RoundLogoB.png" width="200"></td>
<td style="border:0px">
A Python Shape and Geometry Package
<ul>
<li><a href="https://github.com/jhavl/spatialgeometry">GitHub repository </a></li>
<li><a href="https://jhavl.github.io/spatialgeometry">Documentation</a></li>
</ul>
</td>
</tr>
</table>

## Changes in this repository

Compared with the base `jhavl/spatialgeometry` repository, this repository now:

- targets Python 3.10 and newer
- builds and runs against NumPy 2
- includes stricter type hints across the core geometry modules
- ships typing metadata for the compiled `spatialgeometry.scene` extension
- adds `ruff` and `mypy` configuration for static checking
- updates CI to run the new static checks alongside the test suite
- skips optional `roboticstoolbox` integration tests when that upstream dependency is unavailable or incompatible with the active NumPy build

## Development

Install the project and local development dependencies:

```bash
python -m pip install -e '.[dev,collision]'
```

Or create the development environment with `uv` and use the NumPy 2 compatible
`roboticstoolbox-python` fork:

```bash
uv sync --group dev-env --extra collision
uv add --group dev-env "roboticstoolbox-python @ git+https://github.com/gaurishg/robotics-toolbox-python.git"
```

Run the configured checks locally:

```bash
python -m flake8 spatialgeometry tests
python -m ruff check spatialgeometry tests
python -m mypy spatialgeometry
python -m pytest -q
```
