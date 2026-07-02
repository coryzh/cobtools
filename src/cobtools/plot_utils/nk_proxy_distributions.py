import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from importlib import resources
from scipy.stats import maxwell, lognorm
from numpy.typing import ArrayLike
from typing import Tuple


def two_maxwellian(
        x: ArrayLike, sigma1: float, sigma2: float, w: float,
        cumulative: bool = False
) -> ArrayLike:
    """
    Compute the probability density function (PDF) of a double Maxwellian
    distribution.

    Parameters
    ----------
    x : array-like
        The input values at which to evaluate the PDF.
    sigma1 : float
        The scale parameter (standard deviation) of the first Maxwellian
        component.
    sigma2 : float
        The scale parameter (standard deviation) of the second Maxwellian
        component.
    w : float
        The weight of the first Maxwellian component. The weight of the second
        component is (1 - w).

    cumulative : bool, optional
        If True, return the cumulative distribution function (CDF) instead of
        the PDF. Default is False.

    Returns
    -------
    pdf : array-like
        The computed PDF values corresponding to the input `x`.

    Raises
    ------
    ValueError
        If `sigma1` or `sigma2` are not positive, or if `w` is not in the range
        [0, 1].
    """
    if sigma1 <= 0 or sigma2 <= 0:
        raise ValueError(
            "sigma1 and sigma2 must be positive for Maxwellian distribution."
        )

    if w < 0 or w > 1:
        raise ValueError("Weight w must be in the range [0, 1].")

    if cumulative:
        return (
            w * maxwell.cdf(x, scale=sigma1)
            + (1 - w) * maxwell.cdf(x, scale=sigma2)
        )
    else:
        return (
            w * maxwell.pdf(x, scale=sigma1)
            + (1 - w) * maxwell.pdf(x, scale=sigma2)
        )


def lognormal(
        x: ArrayLike, mu: float, sigma: float, cumulative: bool = False
) -> ArrayLike:

    """
    Compute the probability density function (PDF) of a lognormal distribution.

    Parameters
    ----------
    x : array-like
        The input values at which to evaluate the PDF.
    mu : float
        The mean of the underlying normal distribution.
    sigma : float
        The standard deviation of the underlying normal distribution.
    cumulative : bool, optional
        If True, return the cumulative distribution function (CDF) instead of
        the PDF. Default is False.

    Returns
    -------
    pdf : array-like
        The computed PDF values corresponding to the input `x`.

    Raises
    ------
    ValueError
        If `mu` or `sigma` are not positive.
    """

    if mu <= 0 or sigma <= 0:
        raise ValueError(
            "mu and sigma must be positive for velocity distribution."
        )

    if cumulative:
        return lognorm.cdf(x, s=sigma, scale=np.exp(mu))
    else:
        return lognorm.pdf(x, s=sigma, scale=np.exp(mu))


def _load_data() -> pd.DataFrame:
    parameter_file_path = (
        resources.files("cobtools") / "data" / "vpec_dist_compilation.csv"
    )

    df = pd.read_csv(parameter_file_path)
    return df


def make_figure(cumulative: bool = False) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a matplotlib figure for plotting the velocity distribution.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure object.
    ax : matplotlib.axes.Axes
        The created axes object.
    """
    plt.style.use("modernstix")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    ax.set_xlabel("Inferred natal kick (km/s)")
    if cumulative:
        ax.set_ylabel("CDF")
        ax.set_ylim(0, 1.0)
    else:
        ax.set_ylabel("PDF")

    return fig, ax


def add_distribution_to_plot(
        ax: plt.Axes,
        x: ArrayLike,
        row: pd.Series,
        cumulative: bool = False,
        **kwargs
) -> None:
    """
    Add a single distribution to the plot from a data row.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object to which the distribution will be added.
    x : array-like
        The x-values at which to evaluate the distribution.
    row : pd.Series
        A row from the distribution parameter dataframe, with columns
        'type', 'model', 'param1', 'param2', and optionally 'param3'.
    cumulative : bool, optional
        If True, plot the CDF instead of the PDF. Default is False.
    **kwargs
        Additional keyword arguments passed to ax.plot().
    """
    model = row["model"]

    if model == "two_maxwellian":
        y = two_maxwellian(
            x, row["param1"], row["param2"], row["param3"],
            cumulative=cumulative
        )
    elif model == "lognormal":
        y = lognormal(
            x, mu=row["param1"], sigma=row["param2"],
            cumulative=cumulative
        )
    else:
        raise ValueError(f"Unknown model: {model!r}")

    ax.plot(x, y, **kwargs)


def plot_nk_distributions(
        cumulative: bool = False
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Plot natal kick velocity distributions from all references in the
    compiled parameter file.

    Parameters
    ----------
    cumulative : bool, optional
        If True, plot CDFs instead of PDFs. Default is False.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure.
    ax : matplotlib.axes.Axes
        The axes with the plotted distributions.
    """
    df = _load_data()
    fig, ax = make_figure(cumulative=cumulative)
    x = np.linspace(0, 1000, 2000)
    n = len(df)

    cmap = plt.get_cmap("tab10")  # or any other colormap
    lc = [cmap(i / n) for i in range(n)]
    ls = ["-", "--", "-.", ":"] * (n // 4 + 1)  # Repeat line styles if needed
    for i, row in df.iterrows():
        label_text = f"{row['type']} ({row['ref']})"
        add_distribution_to_plot(
            ax, x, row, cumulative=cumulative, linewidth=3.0, alpha=0.8,
            color=lc[i], ls=ls[i], label=label_text
        )

    if cumulative:
        ax.legend(loc="upper right")
    else:
        ax.legend(loc="lower right")

    return fig, ax
