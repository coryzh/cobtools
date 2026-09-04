import click
import numpy as np
from rich.console import Console


def _get_astrometry_from_source_id(
        source_id: int | str, dr: str = "dr3"
) -> dict:
    from cobtools.query.query_gaia import SingleSourceUsefulInfoQuery

    query = SingleSourceUsefulInfoQuery(source_id=source_id, dr=dr)

    try:
        query_results = query.query_result()

    except Exception as e:
        raise click.ClickException(
            f"Error querying Gaia {dr.upper()} for source_id {source_id}: {e}"
        )

    if query_results is not None:
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
    "--dist_method", prompt="Distance estimation method",
    type=click.Choice(["inv", "xrb_exp_prior"]),
    help=(
        "Method to estimate distance from parallax. "
        "'inv' for simple inversion, 'xrb_exp_prior' for XRB exponential "
        "prior."
    ),
)
@click.option(
    "--dr", prompt="Gaia data release (dr2 or dr3)",
    type=click.Choice(["dr2", "dr3"]), default="dr3", show_default=True,
    help="Gaia data release to use for astrometry.",
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
        dist_method: str, conf: float, seed: int | None
) -> None:
    from cobtools.astrometry.kinematics import peculiar_velocity

    np.random.seed(seed)

    with Console().status(
        f"Query Gaia {dr.upper()} for source {source_id}..."
    ):
        astrometry_dict = _get_astrometry_from_source_id(source_id, dr=dr)
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
    display_results(results, conf, n_rand)


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
