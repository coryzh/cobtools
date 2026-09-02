import click
import numpy as np
# from cobtools.astrometry.kinematics import peculiar_velocity


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("ra", type=click.FloatRange(min=0, max=360), metavar="ra")
@click.argument("dec", type=click.FloatRange(min=-90, max=90), metavar="dec")
@click.argument("pmra", type=float, metavar="pmra")
@click.argument(
    "pmra_error", type=click.FloatRange(min=0, min_open=True),
    metavar="pmra_error",
)
@click.argument("pmdec", type=float, metavar="pmdec")
@click.argument(
    "pmdec_error", type=click.FloatRange(min=0, min_open=True),
    metavar="pmdec_error",
)
@click.argument(
    "dist", type=click.FloatRange(min=0, min_open=True), metavar="dist",
)
@click.argument(
    "dist_error", type=click.FloatRange(min=0, min_open=True),
    metavar="dist_error",
)
@click.argument("rv", type=click.FloatRange(min=-3e5, max=3e5), metavar="rv")
@click.argument(
    "rv_error", type=click.FloatRange(min=0, min_open=True),
    metavar="rv_error",
)
@click.option(
    "-c", "--conf", default=0.68,
    type=click.FloatRange(min=0.0, max=1.0, min_open=True, max_open=True),
    help=(
        "Confidence level in decimal form. "
        "Must be between 0 and 1 (exclusive)."
    )
)
@click.option(
    "-n", "--n_samples", default=1000, type=click.IntRange(min=1),
    help="Number of samples to use in the Monte Carlo simulation."
)
def calc_vpec(
        ra: float, dec: float,
        pmra: float, pmra_error: float, pmdec: float, pmdec_error: float,
        dist: float, dist_error: float, rv: float, rv_error: float,
        conf: float, n_samples: int
) -> None:
    """Calculate peculiar velocity (vpec) based on from astrometry

    The user provide the astrometric parameters (ra, dec, pmra, pmdec,
    dist, rv) and the uncertainties on pmra, pmdec, dist, and rv. The
    tool will then generate Monte Carlo samples of the parameters and
    compute the vpec values.

    The user can also specify the confidence level and the number of
    samples to use in the Monte Carlo simulation.

    \b
    ra: Right ascension in decimal degrees. Must be in the range
        [0, 360] degrees.
    dec: Declination in decimal degrees. Must be in the range
        [-90, 90] degrees.
    pmra: Proper motion in right ascension (including the cos(dec)
        factor) in mas/yr.
    pmra_error: Error in proper motion in right ascension in mas/yr.
    pmdec: Proper motion in declination in mas/yr.
    pmdec_error: Error in proper motion in declination in mas/yr.
    dist: Distance in kpc. Must be a positive value.
    dist_error: (no help text was provided for this argument)
    rv: Radial velocity in km/s. Must be in the range [-3e5, 3e5] km/s
        (inclusive).
    rv_error: (no help text was provided for this argument)

    The output is the point estimate and uncertainty of the vpec in
    km/s at the given confidence level.
    """
    pass


def display_results(vpec_sample: np.ndarray, conf: float) -> None:
    pass


if __name__ == "__main__":
    calc_vpec()
