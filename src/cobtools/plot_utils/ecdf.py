import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
from numpy.typing import ArrayLike


def get_ecdf(
        data: ArrayLike, normalised: bool = True
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the empirical cumulative distribution function (ECDF) for 1D data.

    Parameters
    ----------
    data : ArrayLike
        One-dimensional array-like sequence of sample values from which to
        compute the ECDF.
    normalised : bool, optional
        If True (default), the ECDF y-values are normalised to the range
        [0, 1]. If False, y-values are raw counts.

    Returns
    -------
    x : numpy.ndarray
        Sorted data values prepared for step plotting. The smallest value is
        duplicated at the start so that the first ECDF step begins at the
        minimum x-value.
    y : numpy.ndarray
        ECDF values corresponding to ``x``. If ``normalised`` is True,
        ``y`` ranges from 0 to 1; otherwise, it contains cumulative counts
        from 0 up to ``len(data)``.

    Raises
    ------
    ValueError
        If the input array is empty or not one-dimensional.
    """
    data = np.asarray(data)

    if len(data) == 0:
        raise ValueError("Input array must not be empty.")

    if data.ndim != 1:
        raise ValueError("Input array must be one-dimensional.")

    x = np.sort(data)
    y = np.arange(0, len(x) + 1)

    if normalised:
        y = y / float(len(x))

    # Duplicate the smallest x so the ECDF starts at y=0; if normalised=True,
    # the final step ends at 1 (otherwise at len(x)).
    x = np.insert(x, 0, x[0])  # Duplicate the smallest x-value

    return x, y


def plot_ecdf(
        data: ArrayLike, ax: plt.Axes,
        bounds: Tuple[np.ndarray, np.ndarray] = None, normalised: bool = True,
        **kwargs
) -> None:
    x, y = get_ecdf(data, normalised=normalised)
    if bounds:
        arr_lo, arr_up = bounds
        x_lo, y_lo = get_ecdf(arr_lo, normalised=normalised)
        x_up, y_up = get_ecdf(arr_up, normalised=normalised)

        ax.step(x, y, where="post", lw=1.5, **kwargs)
        ax.step(x_lo, y_lo, where="post", lw=1.0, ls=":")
        ax.step(x_up, y_up, where="post", lw=1.0, ls=":")

    else:
        ax.step(x, y, where="post", **kwargs)
