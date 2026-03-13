# cobtools

This is a software package hosting the utility functions and tools I used in my 
research. 

## Features
- Astrometry & Kinematics
    - Distance inference based on parallax and parallax uncertainty
    - Compute space velocity and peculiar velocities given astrometric parameters

- Photometry
    - Interpret Gaia color indices as effective temperature.

- Plotting
    - Plot empirical cumulative distribution function

## Installation
First, clone the repository to your machine:
```bash
git clone https://github.com/coryzh/cobtools.git
cd cobtools
```

Install the package in editable mode:

```bash
pip install -e .
```
The "editable" mode (indicated by the -e flag) means that changes to the source code will immediately reflect in the installed package.

To verify the package is installed correctly open a Python shell and import the package

```
python
>>> import cobtools
>>> print(cobtools.__version__)
```

## Development

For development, install development dependencies by running
```bash
pip install -e .[dev]
```
