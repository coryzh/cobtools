#!/usr/bin/env python3

import click
import numpy as np

METHOD_LABELS = {
    "inv": "Inverted parallax",
    "xrb_exp_prior": "Bayesian (XRB exponential prior)",
}


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Get parallax-based distance estimates (in kpc)\n\n"
         "User input the parallax and parallax_error in mas and specify the "
         "method used to derive the distance. The output is the distance in "
         "kpc and the associated uncertainty at the confidence level "
         "specified by the user."
)
@click.argument(
    "parallax", type=float, metavar="parallax"
)
@click.argument(
    "parallax_error", type=click.FloatRange(min=0, min_open=True),
    metavar="parallax_error"
)
@click.option(
    "--method",
    default="inv",
    show_default=True,
    type=click.Choice(
        list(METHOD_LABELS.keys()), case_sensitive=False
    ),
    help=(
        "Method used to derive the distance from the parallax. "
        f"Valid options are: {', '.join(METHOD_LABELS.keys())}. "
        f"'inv' is to directly invert the parallax, and 'xrb_exp_prior' is to "
        "derive distance from the posterior distribution using the "
        "exponential prior for X-ray binaries (e.g., Zhao et al. 2023)."
    )
)
@click.option(
    "--conf",
    default=0.68,
    show_default=True,
    type=float,
    help=(
        "Confidence level for the output distance uncertainty in decimal "
        "form, which should be a value between 0 and 1. The default is 0.68, "
        r"i.e., 68% confidence level, the lower and upper errors will be "
        "calculated at the 16th and 84th percentiles of the sampled "
        "distribution, and the point estimate will be the median."
    )
)
def estimate_distance(
    parallax: float, parallax_error: float, method: str, conf: float
) -> None:
    """
    Estimate distance from user-input arguments.

    Parameters
    ----------
    parallax : float
        User-input parallax in mas.
    parallax_error : float
        User-input parallax error in mas.
    method : str
        User-input method string.
    conf : float
        User-input decimal confidence level between 0 and 1.

    Raises
    ------
    click.UsageError
        If the confidence level is not between 0 and 1, or if the method is
        not recognized.
    """
    if conf <= 0 or conf >= 1:
        raise click.UsageError(
            f"Invalid confidence level '{conf}'. "
            "It should be a value between 0 and 1."
        )

    from cobtools.astrometry.distance import (
        SimpleInversion,
        XRBExponentialPriorModel
    )

    if method == "inv":
        if parallax < 0 or parallax / parallax_error < 5:
            click.secho(
                "Warning: The parallax is negative or has a low SNR (<5). "
                "The inverted parallax estimate may be unreliable.",
                fg="yellow",
                err=True,
            )
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

    display_results(dist_sample, conf, method)


def display_results(dist_arr: np.ndarray, conf: float, method: str) -> None:
    """Display point estimate and confidence interval of the distance.

    Parameters
    ----------
    dist_arr : np.ndarray
        Array of sampled distances in kpc.

    conf : float
        Decimal confidence level (between 0 and 1).

    method : str
        Method string.
    """

    percentiles = [(1 - conf) / 2 * 100, 50, (1 + conf) / 2 * 100]

    d_lo, d_est, d_hi = np.percentile(dist_arr, percentiles)
    d_lo_err = d_est - d_lo
    d_hi_err = d_hi - d_est

    click.echo(
        f"Distance (median): {d_est:.2f} "
        f"+{d_hi_err:.2f}/-{d_lo_err:.2f} kpc\n"
        f"{conf * 100:.0f}% equal-tailed interval: "
        f"[{d_lo:.2f}, {d_hi:.2f}] kpc \n"
        f"Method: {METHOD_LABELS[method]}"
    )


if __name__ == "__main__":
    estimate_distance()
