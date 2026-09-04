import click
import numpy as np
from rich.console import Console


def _get_astrometry_from_source_id(
        source_id: int, dr: str = "dr3"
) -> dict:
    from cobtools.query.query_gaia import SingleSourceUsefulInfoQuery

    query = SingleSourceUsefulInfoQuery(source_id=source_id, data_release=dr)

    try:
        query_results = query.query_result()

    except Exception as e:
        raise click.ClickException(
            f"Error querying Gaia {dr.upper()} for source_id {source_id}: {e}"
        )

    if query_results is not None and len(query_results) > 0:
        cols = [
            "source_id", "ra", "dec", "parallax", "parallax_error",
            "pmra", "pmra_error", "pmdec", "pmdec_error",
        ]
        result_row = query_results[0]
        result_dict = {
            col: result_row[col] for col in cols
        }
    else:
        raise click.ClickException(
            f"No results found for source_id {source_id} in Gaia {dr.upper()}."
        )

    return result_dict


def _get_distance_samples(
        parallax: float, parallax_error: float, method: str = "inv"
) -> np.ndarray:
    from cobtools.astrometry.distance import (
        SimpleInversion,
        XRBExponentialPriorModel
    )

    if method == "inv":
        dist_mod = SimpleInversion(parallax, parallax_error)
        dist_sample = dist_mod.sample_distance(n_samples=10000)

    elif method == "xrb_exp_prior":
        dist_mod = XRBExponentialPriorModel(parallax, parallax_error)
        dist_sample = dist_mod.sample_distance()

    else:
        raise click.UsageError(
            f"Unknown method '{method}'. "
            "Valid options are 'inv' and 'xrb_exp_prior'."
        )

    return dist_sample


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option(
    "--source_id", prompt="Gaia source ID", type=click.INT,
    help="Gaia source_id for which to calculate the peculiar velocity.",
)
@click.option(
    "--dr", prompt="Gaia data release (dr2 or dr3)",
    type=click.Choice(["dr2", "dr3"]), default="dr3", show_default=True,
    help="Gaia data release to use for astrometry.",
)
@click.option(
    "--rv", prompt="Radial velocity (km/s)",
    type=click.FloatRange(min=-3e5, max=3e5),
    help=(
        "Radial velocity in km/s. Must be in the range [-3e5, 3e5] km/s "
        "(inclusive)."
    ),
)
@click.option(
    "--rv_error", prompt="1-sigma error in radial velocity (km/s)",
    type=click.FloatRange(min=0, min_open=True),
    help="1-sigma error in radial velocity in km/s.",
)
@click.option(
    "--dist_source", prompt="Distance source (gaia or user)",
    type=click.Choice(["gaia", "user"]),
    help=(
        "Source of distance information. 'gaia' uses Gaia parallax to "
        "estimate distance, while 'user' uses user-provided distance and "
        "error."
    ),
    default="gaia",
    show_default=True
)
@click.option(
    "--dist_method", default=None,
    type=click.Choice(["inv", "xrb_exp_prior"]),
    help=(
        "Method to estimate distance from parallax, used only when "
        "--dist_source=gaia. Options are "
        "'inv' for simple inversion, 'xrb_exp_prior' for XRB exponential "
        "prior."
    ),
)
@click.option(
    "--dist", default=None,
    type=click.FloatRange(min=0, min_open=True),
    help=(
        "Distance in kpc. Must be a positive value. Used only when "
        "--dist_source='user'."
    ),
)
@click.option(
    "--dist_error", default=None,
    type=click.FloatRange(min=0, min_open=True),
    help=(
        "1-sigma error in distance in kpc. Must be a positive number. Used "
        "only when --dist_source='user'."
    ),
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
    "-s", "--seed", default=42, type=click.IntRange(min=0, max=2**32 - 1),
    help="Random seed for reproducibility."
)
def calc_vpec(
        source_id: int | str, dr: str, rv: float, rv_error: float,
        dist_source: str, dist: float | None, dist_error: float | None,
        dist_method: str | None, conf: float, seed: int | None
) -> None:
    """Calculate peculiar velocity (vpec) for a Gaia source_id.

    Queries the Gaia archive for the astrometric parameters (ra, dec,
    pmra, pmdec, parallax) of the given source_id, combines them with a
    user-supplied radial velocity (and its error), and generates Monte
    Carlo samples to compute the vpec and its Cartesian (U, V, W)
    components.

    Distance can come from two sources, selected via --dist_source:

    \b
    - 'gaia': distance is inferred from the Gaia parallax using the
      method chosen via --dist_method ('inv' or 'xrb_exp_prior').
    - 'user': distance and its 1-sigma error are supplied directly by
      the user (via --dist/--dist_error or an interactive prompt).

    Any option omitted on the command line will be prompted for
    interactively; --dist_method, --dist, and --dist_error are only
    prompted for when relevant to the chosen --dist_source.

    The output is the point estimate and the uncertainty of the distance (kpc),
    vpec, and its Cartesian components in km/s at the given confidence
    level. The uncertainties correspond to equal-tailed intervals at the
    specified confidence level.
    """

    from cobtools.astrometry.kinematics import peculiar_velocity

    np.random.seed(seed)

    with Console().status(
        f"Query Gaia {dr.upper()} for source {source_id}..."
    ):
        astrometry_dict = _get_astrometry_from_source_id(source_id, dr=dr)

    if dist_source == "user":
        if dist is None:
            dist = click.prompt(
                "Distance (kpc)", type=click.FloatRange(min=0, min_open=True)
            )

        if dist_error is None:
            dist_error = click.prompt(
                "1-sigma error in distance (kpc)",
                type=click.FloatRange(min=0, min_open=True)
            )

        dist_rand = np.random.normal(dist, dist_error, 10000)
    else:
        if dist_method is None:
            dist_method = click.prompt(
                "Distance estimation method",
                type=click.Choice(["inv", "xrb_exp_prior"])
            )
        dist_rand = _get_distance_samples(
            astrometry_dict["parallax"],
            astrometry_dict["parallax_error"],
            method=dist_method
        )

    n_rand = len(dist_rand)
    ra = astrometry_dict["ra"]
    dec = astrometry_dict["dec"]
    pmra = astrometry_dict["pmra"]
    pmra_error = astrometry_dict["pmra_error"]
    pmdec = astrometry_dict["pmdec"]
    pmdec_error = astrometry_dict["pmdec_error"]

    pmra_rand = np.random.normal(pmra, pmra_error, n_rand)
    pmdec_rand = np.random.normal(pmdec, pmdec_error, n_rand)

    rv_rand = np.random.normal(rv, rv_error, n_rand)

    results = peculiar_velocity(
        ra=ra, dec=dec, pmra_cosdec=pmra_rand, pmdec=pmdec_rand,
        dist=dist_rand, rv=rv_rand
    )

    # Pack the distance samples with the results for display
    # results[0] corresponds to the distance samples.
    results = np.vstack((dist_rand, results))

    display_results(results, conf, n_rand)


def display_results(
        results: np.ndarray, conf: float, n_samples: int
) -> None:
    labels = ("dist", "U", "V", "W", "vpec")
    units = ("kpc", "km/s", "km/s", "km/s", "km/s")
    percentiles = [(1 - conf) / 2 * 100, 50, (1 + conf) / 2 * 100]

    lines = []
    for label, unit, sample in zip(labels, units, results):
        lo, est, hi = np.percentile(sample, percentiles)
        lo_err, hi_err = est - lo, hi - est
        lines.append(
            f"{label:>4}: {est:8.2f} +{hi_err:.2f}/-{lo_err:.2f} {unit}  "
            f"[{lo:.2f}, {hi:.2f}] {unit} ({conf * 100:.0f}% CI)"
        )

    click.echo("\n".join(lines))
    click.echo(f"Number of samples: {n_samples}")


if __name__ == "__main__":
    calc_vpec()
