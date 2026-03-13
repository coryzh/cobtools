import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from typing import Union
from importlib import resources


def _load_coefficients() -> pd.DataFrame:
    coefficient_file_path = (
        resources.files("cobtools.data") / "bprp_to_teff_coefficients.csv"
    )
    return pd.read_csv(coefficient_file_path, index_col="kind")


df_coefs = _load_coefficients()


def bp_rp_to_teff(
    bp_rp: Union[float, ArrayLike], mh: Union[float, ArrayLike] = 0.0,
    kind: str = "dwarf"
) -> Union[float, ArrayLike]:
    """
    Convert Gaia BP-RP color index to effective temperature (Teff) using
    polynomial coefficients from Mucciarelli et al. (2021).

    Parameters
    ----------
    bp_rp : Union[float, ArrayLike]
        Gaia BP-RP color index.
    mh : Union[float, ArrayLike], optional
        Metallicity, by default 0.0 (solar metallicity).
    kind : str, optional
        Kind of star, by default "dwarf"

    Returns
    -------
    Union[float, ArrayLike]
        Effective temperature (Teff) in Kelvin.

    Raises
    ------
    TypeError
        If the input parameters are not of the expected type or cannot be
        converted to the expected type.
    ValueError
        If the input parameters are out of bounds or invalid.
    ValueError
        If the kind is not valid.
    ValueError
        If the input arrays have different shapes.
    """
    if not isinstance(kind, str):
        raise TypeError(f"kind must be a string, got {type(kind)}")

    if kind not in df_coefs.index:
        raise ValueError(
            f"Invalid kind '{kind}'. "
            f"Valid options are: {df_coefs.index.tolist()}"
        )

    row = df_coefs.loc[kind]
    bp_rp_min, bp_rp_max = row["bp_rp_min"], row["bp_rp_max"]

    try:
        bp_rp = np.asarray(bp_rp, dtype=float)
    except Exception as e:
        raise TypeError(
            f"bp_rp must be convertible to a numpy array of float: {e}"
        )

    try:
        mh = np.asarray(mh, dtype=float)
    except Exception as e:
        raise TypeError(
            f"mh must be convertible to a numpy array of float: {e}"
        )

    # Make mh broadcastable to bp_rp
    if np.isscalar(mh) or mh.ndim == 0:
        mh = np.full_like(bp_rp, fill_value=mh)

    if bp_rp.shape != mh.shape:
        raise ValueError(
            f"bp_rp and mh must have the same shape, got {bp_rp.shape} "
            f"for bp_rp but {mh.shape} for mh."
        )

    if np.any((bp_rp < bp_rp_min) | (bp_rp > bp_rp_max)):
        raise ValueError(
            f"bp_rp must be between {bp_rp_min} and {bp_rp_max} for '{kind}'"
        )

    coeff_cols = ["b0", "b1", "b2", "b3", "b4", "b5"]

    coeffs = row[coeff_cols].values

    teff = 5040.0 / (
        coeffs[0] + coeffs[1] * bp_rp + coeffs[2] * bp_rp ** 2
        + coeffs[3] * mh + coeffs[4] * mh ** 2 + coeffs[5] * bp_rp * mh
    )

    if bp_rp.ndim == 0:
        teff = float(teff)

    return teff
