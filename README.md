# cobtools

`cobtools` is a software package hosting the utility tools that I commonly use
in my research.

## Features
- Astrometry & Kinematics
    - Parallax-based distance inference.
    - Computation of peculiar velocities.

- Conversion
    - Conversion between magnitudes and fluxes.
    - Conversion between different colour indices and stellar spectral types.

- Data API wrappers
    - Lasair LSST API wrapper: A wrapper client to query and parse the raw API data
    - Gaia query: Wrapper around the `astroquery.Gaia` module for getting Gaia data for individual sources.

- Plotting
    - Gaia CMD plotter: customised `matplotlib.Axes` with a pre-plotted background.
    of scatter.
    - ECDF plotter: A helper function for plotting the empirical cumulative distribution function (ECDF) of a given data array.

## Installation
To install, first, clone the repository to your machine:

```bash
git clone https://github.com/coryzh/cobtools.git
cd cobtools
```

Then, install the package in editable mode:
```bash
pip install -e .
```

Then, install the package in editable mode:

```bash
pip install -e .
```

The "editable" mode (indicated by the `-e` flag) means that changes to the source code will be immediately reflected in the installed package.

To verify the package is installed correctly, open a Python shell and import the package:

```python
python
>>> import cobtools
>>> print(cobtools.__version__)
```

The "editable" mode (indicated by the `-e` flag) means that changes to the source code will immediately reflect in the installed package.

To verify the package is installed correctly open a Python shell and import the package


```python
python
>>> import cobtools
>>> print(cobtools.__version__)
```

## Documentation
The API documentation is available [here](coryzh.github.io/cobtools).

To build the documentation locally, navigate to the `docs/` folder and run:
```bash
make html
```
The generated HTML files will be located in `docs/build/html/`


## Testing
Unit tests are located in tests/ folder and can be performed with `pytest`, e.g.,
```bash
pytest tests/test_flux_conversion.py
```

## Development
For development, install development dependencies by running
```bash
pip install -e .[dev]
```


## Contributing
We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Write your code and add tests.
4. Submit a pull request.

Please ensure your code follows the existing style and passes all tests.

## Acknowledgments
This project makes use of the following libraries:
- [astroquery](https://astroquery.readthedocs.io/)
- [asropy](https://www.astropy.org/index.html)
- [lasair](https://lasair-lsst.readthedocs.io/en/develop/core_functions/client.html)
- [matplotlib](https://matplotlib.org/)
- [numPy](https://numpy.org/)
- [pandas](https://pandas.pydata.org/)
- [scipy](https://docs.scipy.org/doc/scipy/)
