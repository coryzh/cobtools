# cobtools

`cobtools` is a software package hosting the utility tools that I commonly use in my research of compact-object binaries (COBs).

## Features
- Astrometry & Kinematics
    - Parallax-based distance inference.
    - Computation of peculiar velocities.

- Photometric tools
    - Conversion between magnitudes and fluxes.
    - Conversion between different colour indices and stellar spectral types.

- Data API wrappers
    - Lasair LSST API wrapper: A wrapper client to query and parse the raw API data
    - Gaia query: Wrapper around the `astroquery.Gaia` module for getting Gaia data for individual sources.

- Plotting
    - Gaia CMD plotter: customised `matplotlib.Axes` with a pre-plotted background of scatter.
    - ECDF plotter: A helper function for plotting the empirical cumulative distribution function (ECDF) of a given data array.
    - Plotting script to display and generate cumulative distributions of natal kicks from various studies.

- Command-line interfaces
    - `gaia_single_source`: Display essential Gaia columns for a given Gaia `source_id`.
    - `par_to_dist`: Display parallax-based distance estimates and associated uncertainties.
    - `vpec_from_astrometry`: Display estimates and uncertainties for the peculiar velocity and its Cartesian components from astrometric parameters.
    - `vpec_from_source_id`: Display estimates and uncertainties for the peculiar velocity and its Cartesian components for a given Gaia `source_id` and radial velocity.

## Installation

`cobtools` requires Python >= 3.10 and the following packages:

| Package | Minimum Version |
|---------|----------------|
| `numpy` | 2.0.0 |
| `matplotlib` | 3.9.2 |
| `scipy` | 1.14.1 |
| `emcee` | 3.1.6 |
| `pandas` | 2.2.1 |
| `astroquery` | 0.4.10 |
| `lasair` | 0.1.2 |
| `click` | 8.0.0 |
| `platformdirs` | 4.3.6 |
| `rich` | 13.0.0 |

It is recommended to install `cobtools` in a dedicated virtual environment to avoid dependency conflicts with other packages.
### Install uv
The virtual environment is managed by `uv`. To install uv, follow the [official guide](https://docs.astral.sh/uv/getting-started/installation/). In general, it is recommended to use the installation script. For Linux or MacOS, for example, run

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```


### Creating a virtual environment
Then, clone the repository to your machine:

```bash
git clone https://github.com/coryzh/cobtools.git
cd cobtools
```

Then, install the package using `uv`
```bash
uv sync --extra dev
```
This will install the package in editable mode. `--extra dev` will include the extra tools for development (`pytest`, `ruff`, etc.).

<details>
<summary>What is editable mode?</summary>

The "editable" mode means that changes to the source code will immediately reflect in the installed package.

</details>

### Verify installation
To verify the package is installed correctly, open a terminal and run:

```bash
uv run python -c "import cobtools; print(cobtools.__version__)"
```
This should print out the version number of the package.

## Updating
To update the package, pull the latest changes from the branch and re-run the `uv` command.

```bash
cd cobtools
git pull
uv sync --extra dev
```

## Using the command-line interfaces

After installation, the command-line interfaces are available from the terminal. There are two ways to use these commands. To activate the environment and run commands directly

```bash
source .venv/bin/activate
```
then
```bash
<command-name>
```

Alternatively, you can prefix the commands with `uv run` without activating the virtual environment, i.e.,
```bash
uv run <command-name>
```

### Query a Gaia source
Display selected Gaia columns for a source from Gaia DR3:

```bash
uv run gaia_single_source <source_id> --dr dr3
```

By default, query results are cached. Use `--no-cache` to bypass the cache:

```bash
uv run gaia_single_source <source_id> --dr dr3 --no-cache
```

### Estimate distance from parallax

Provide the parallax and its uncertainty in milliarcseconds. The default method is direct parallax inversion:

```bash
uv run par_to_dist 1.25 0.10
```

To use the X-ray binary exponential-prior model instead:

```bash
uv run par_to_dist 1.25 0.10 --method xrb_exp_prior
```

Use `--conf` to change the confidence level for the reported uncertainty:

```bash
uv run par_to_dist 1.25 0.10 --conf 0.95
```

### Calculate peculiar velocity from astrometry

`vpec_from_astrometry` prompts interactively for any astrometric values that are not provided on the command line. For example:

```bash
uv run vpec_from_astrometry
```

Options can also be supplied explicitly:

```bash
uv run vpec_from_astrometry \
    --ra 83.63 --dec 22.01 \
    --pmra 5.2 --pmra_error 0.3 \
    --pmdec -2.1 --pmdec_error 0.2 \
    --dist 2.0 --dist_error 0.1 \
    --rv 35.0 --rv_error 2.0
```

### Calculate peculiar velocity from a Gaia source

 This command retrieves astrometric parameters for the specified Gaia source and uses the provided radial velocity and its uncertainty (prompting for them if omitted):

```bash
uv run vpec_from_source_id --source_id <source_id> --dr dr3 --rv 35.0 --rv_error 2.0
```

By default, the distance is estimated from the Gaia parallax. To provide a
user-supplied distance instead, use `--dist_source user` together with
`--dist` and `--dist_error`:

```bash
uv run vpec_from_source_id \
    --source_id Gaia-source-id --dr dr3 \
    --rv 35.0 --rv_error 2.0 \
    --dist_source user --dist 2.0 --dist_error 0.1
```

## Documentation
The API documentation is available [here](https://coryzh.github.io/cobtools).

To build the documentation locally, `cd` to the repository root, then:
```bash
uv run --extra dev make -C docs html
```
The generated HTML files will be located in `docs/build/html/`


## Testing
Unit tests are located in tests/ folder and can be performed with `pytest`, e.g.,
```bash
uv run --extra dev pytest tests/test_flux_conversion.py
```

To run all tests in `tests/`
```bash
uv run --extra dev pytest
```


## Contributing
To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Write your code and add tests to `tests/`.
4. Submit a pull request.

Please ensure your code follows the existing style and passes all tests.

If you find any issues or have suggestions for improvements, please [open an issue](https://github.com/coryzh/cobtools/issues) with a clear description of the problem or feature request.

## Acknowledgments
Development was assisted by [GitHub Copilot](https://github.com/features/copilot).

This project makes use of the following libraries.
- [astroquery](https://astroquery.readthedocs.io/)
- [astropy](https://www.astropy.org/index.html)
- [lasair](https://lasair-lsst.readthedocs.io/en/develop/core_functions/client.html)
- [matplotlib](https://matplotlib.org/)
- [NumPy](https://numpy.org/)
- [pandas](https://pandas.pydata.org/)
- [scipy](https://docs.scipy.org/doc/scipy/)
- [platformdirs](https://platformdirs.readthedocs.io/en/latest/)
