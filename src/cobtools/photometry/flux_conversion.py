import numpy as np
from numpy.typing import ArrayLike
from typing import Union
from cobtools.data_models.band import Band


def magnitude_to_flux(
        mag: Union[float, ArrayLike], band: Band
) -> np.ndarray:
    """
    Convert magnitude to flux for a given band

    Parameters
    ----------
    mag : Union[float, ArrayLike]
        Magnitude(s) to convert
    band : Band
        Band for which to convert magnitude to flux. Must be a Band instance.

    Returns
    -------
    np.ndarray
        Flux(es) in erg/s/cm^2

    Raises
    ------
    ValueError
        If mag is not a float or array-like of floats, or if it contains
        non-finite or non-positive values.

    TypeError
        If band is not an instance of Band.

    Notes
    -----
    The conversion is done using the formula:
    .. math::
        F = F_0 * w_eff * 10^{-0.4 * m},
    where :math:`F_0` is the zero-point flux for the band, :math:`w_eff` is
    the effective wavelength, and :math:`m` is the magnitude. F0 values are
    from Gaia Collaboration (2021), A&A, 639, A3.
    """

    try:
        mag = np.asarray(mag, dtype=np.float64)

    except (TypeError, ValueError) as e:
        raise ValueError(
            f"mag must be a float or array-like of floats: {e}"
        ) from e

    if mag.ndim > 1:
        raise ValueError("mag must be a scalar or 1D array.")

    if not np.all(np.isfinite(mag)) or np.any(mag <= 0):
        raise ValueError("mag must contain finite positive values.")

    if not isinstance(band, Band):
        raise TypeError(
            f"band must be an instance of Band, but got {type(band)}."
        )

    flam = band.zp_flam * band.w_eff * 10 ** (-0.4 * mag)

    return flam
