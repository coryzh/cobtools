import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from typing import Union, List
from importlib import resources


def _load_coefficients() -> pd.DataFrame:
    coefficient_file_path = (
        resources.files("cobtools") / "data" / "bprp_to_teff_coefficients.csv"
    )
    return pd.read_csv(coefficient_file_path, index_col="kind")


def _load_sptypes() -> pd.DataFrame:
    sptype_file_path = (
        resources.files("cobtools") / "data" / "teff_and_sptype.csv"
    )
    return pd.read_csv(sptype_file_path)


df_coefs = _load_coefficients()
df_sptypes = _load_sptypes()


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


def bp_rp_to_sptype(
        bp_rp: Union[float, ArrayLike], mh: Union[float, ArrayLike] = 0.0,
        kind: str = "dwarf"
) -> Union[str, List[str]]:
    """
    Convert Gaia BP-RP color index to spectral type using the Teff derived
    from bp_rp_to_teff and the Teff-SpType relation from Pecaut & Mamajek
    (2013).

    Parameters
    ----------
    bp_rp : Union[float, ArrayLike]
        Gaia BP-RP color index.
    mh : Union[float, ArrayLike], optional
        Metallicity, by default 0.0 (solar metallicity).
    kind : str, optional
        Kind of star, by default "dwarf". Valid options are "dwarf" and "giant"

    Returns
    -------
    Union[str, List[str]]
        Spectral type. If the input is a single value, returns a string.
        If the input is an ArrayLike, returns a list of strings.

    Raises
    ------
    ValueError
        If the calculated effective temperature is out of the valid range for
        spectral type determination.
    """

    teff_min, teff_max = df_sptypes["Teff"].min(), df_sptypes["Teff"].max()

    teff = bp_rp_to_teff(bp_rp, mh, kind)

    if np.any((teff < teff_min) | (teff > teff_max)):
        raise ValueError(
            f"Calculated Teff must be between {teff_min} and {teff_max} K "
            f"to determine spectral type, but got Teff={teff} K."
        )

    if np.isscalar(teff):
        idx_closest = np.argmin(np.abs(df_sptypes["Teff"] - teff))
        return df_sptypes.loc[idx_closest, "SpType"]
    else:
        idx_closest = np.abs(
            df_sptypes["Teff"].values[:, None] - teff
        ).argmin(axis=0)

        sptypes = df_sptypes.iloc[idx_closest]["SpType"].tolist()

        return sptypes
