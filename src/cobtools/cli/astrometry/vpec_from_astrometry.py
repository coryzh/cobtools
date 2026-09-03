import click
import numpy as np
from cobtools.astrometry.kinematics import peculiar_velocity


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option(
    "--ra", prompt="Right ascension (deg)",
    type=click.FloatRange(min=0, max=360, max_open=True),
    help="Right ascension in decimal degrees. Range [0, 360) degrees.",
)
@click.option(
    "--dec", prompt="Declination (deg)",
    type=click.FloatRange(min=-90, max=90),
    help="Declination in decimal degrees. Range [-90, 90] degrees.",
)
@click.option(
    "--pmra", prompt="Proper motion in RA (mas/yr)", type=float,
    help=(
        "Proper motion in right ascension (including the cos(dec) "
        "factor) in mas/yr."
    ),
)
@click.option(
    "--pmra_error", prompt="1-sigma error in pmra (mas/yr)",
    type=click.FloatRange(min=0, min_open=True),
    help="1-sigma error in proper motion in ra in mas/yr.",
)
@click.option(
    "--pmdec", prompt="Proper motion in Dec (mas/yr)", type=float,
    help="Proper motion in declination in mas/yr.",
)
@click.option(
    "--pmdec_error", prompt="1-sigma error in pmdec (mas/yr)",
    type=click.FloatRange(min=0, min_open=True),
    help="1-sigma error in proper motion in declination in mas/yr.",
)
@click.option(
    "--dist", prompt="Distance (kpc)",
    type=click.FloatRange(min=0, min_open=True),
    help="Distance in kpc. Must be a positive value.",
)
@click.option(
    "--dist_error", prompt="1-sigma error in distance (kpc)",
    type=click.FloatRange(min=0, min_open=True),
    help="1-sigma error in distance in kpc.",
)
@click.option(
    "--rv", prompt="Radial velocity (km/s)",
    type=click.FloatRange(min=-3e5, max=3e5),
    help=(
        "Radial velocity in km/s. Must be in the range [-3e5, 3e5] "
        "km/s (inclusive)."
    ),
)
@click.option(
    "--rv_error", prompt="1-sigma error in radial velocity (km/s)",
    type=click.FloatRange(min=0, min_open=True),
    help="1-sigma error in radial velocity in km/s.",
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
@click.option(
    "-s", "--seed", default=42, type=click.IntRange(min=0, max=2**32 - 1),
    help="Random seed for reproducibility."
)
def calc_vpec(
        ra: float, dec: float,
        pmra: float, pmra_error: float, pmdec: float, pmdec_error: float,
        dist: float, dist_error: float, rv: float, rv_error: float,
        conf: float, n_samples: int, seed: int | None
) -> None:
    """Calculate peculiar velocity (vpec) based on astrometry

    The user provides the astrometric parameters (ra, dec, pmra, pmdec,
    dist, rv) and the uncertainties on pmra, pmdec, dist, and rv. The
    tool will then generate Monte Carlo samples of the parameters and
    compute the vpec values.

    The user can also specify the confidence level and the number of
    samples to use in the Monte Carlo simulation.

    Any option omitted on the command line will be prompted for
    interactively.

    The output is the point estimate and uncertainty of the vpec and its
    Cartesian components in km/s at the given confidence level.
    """
    np.random.seed(seed)

    pmra_rand = np.random.normal(pmra, pmra_error, n_samples)
    pmdec_rand = np.random.normal(pmdec, pmdec_error, n_samples)
    dist_rand = np.random.normal(dist, dist_error, n_samples)
    rv_rand = np.random.normal(rv, rv_error, n_samples)

    results = peculiar_velocity(
        ra=ra, dec=dec, pmra_cosdec=pmra_rand, pmdec=pmdec_rand,
        dist=dist_rand, rv=rv_rand
    )

    display_results(results, conf, n_samples)


def display_results(
        results: np.ndarray, conf: float, n_samples: int
) -> None:
    labels = ("U", "V", "W", "vpec")
    percentiles = [(1 - conf) / 2 * 100, 50, (1 + conf) / 2 * 100]

    lines = []
    for label, sample in zip(labels, results):
        lo, est, hi = np.percentile(sample, percentiles)
        lo_err, hi_err = est - lo, hi - est
        lines.append(
            f"{label:>4}: {est:8.2f} +{hi_err:.2f}/-{lo_err:.2f} km/s  "
            f"[{lo:.2f}, {hi:.2f}] km/s ({conf * 100:.0f}% CI)"
        )

    click.echo("\n".join(lines))
    click.echo(f"Number of samples: {n_samples}")


if __name__ == "__main__":
    calc_vpec()
