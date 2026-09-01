#!/usr/bin/env python3

import click
import numpy as np


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
    "parallax_error", type=float, metavar="parallax_error"
)
@click.option(
    "--method",
    default="inv",
    show_default=True,
    type=click.Choice(
        ["inv", "xrb_exp_prior"]
    ),
    help=(
        "Method used to derive the distance from the parallax. "
        "'inv' is to directly invert the parallax, and 'xrb_exp_prior' is to "
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
    """placeholder function for the estimate_distance command."""
    from cobtools.astrometry.distance import (
        SimpleInversion,
        XRBExponentialPriorModel
    )
    if conf <= 0 or conf >= 1:
        raise click.UsageError(
            f"Invalid confidence level '{conf}'. "
            "It should be a value between 0 and 1."
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
        click.echo(
            f"Distance estimate: {dist_mod.d_est: .2f} "
            f"+/- {dist_mod.d_est_error:.2f} kpc"
        )
    elif method == "xrb_exp_prior":
        dist_mod = XRBExponentialPriorModel(parallax, parallax_error)

        dist_sample = dist_mod.sample_distance()
        d_lo, d_est, d_hi = np.percentile(dist_sample, [16, 50, 84])
        d_lo_err = d_est - d_lo
        d_hi_err = d_hi - d_est
        click.echo(
            f"Distance estimate: {d_est: .2f} "
            f"+{d_hi_err:.2f} / -{d_lo_err:.2f} kpc"
        )

    else:
        raise click.UsageError(
            f"Unknown method '{method}'. "
            "Valid options are 'inv' and 'xrb_exp_prior'."
        )


if __name__ == "__main__":
    estimate_distance()
