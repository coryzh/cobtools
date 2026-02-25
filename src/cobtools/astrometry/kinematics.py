import numpy as np
import cobtools.constants as con
from typing import Tuple, Union
from numpy.typing import ArrayLike


def equatorial_to_galactic(
        ra: Union[float, ArrayLike], dec: Union[float, ArrayLike]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert equatorial coordinates (RA, Dec) to galactic coordinates (l, b).
    Parameters
    ----------
    ra : float or ArrayLike
        Right ascension in decimal degrees.
    dec : float or ArrayLike
        Declination in decimal degrees.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Galactic longitude (l) and latitude (b) in decimal degrees.
        If inputs are scalars, outputs will be numpy scalars.

    Raises
    ------
    ValueError
        If RA and Dec have different shapes, or if RA is not in [0,
        360) degrees, or if Dec is not in [-90, 90] degrees.
    """

    ra = np.array(ra, ndmin=1)
    dec = np.array(dec, ndmin=1)

    if np.shape(ra) != np.shape(dec):
        raise ValueError("RA and Dec must have the same shape.")

    if np.any((ra < 0) | (ra >= 360)):
        raise ValueError(
            "Input right ascension must be in the range [0, 360) degrees."
        )

    if np.any((dec < -90) | (dec > 90)):
        raise ValueError(
            "Input declination must be in the range [-90, 90] degrees."
        )

    # Source coordinates to radian
    ra_rad, dec_rad = np.radians(ra), np.radians(dec)

    # This part compute the Galactic coordinates of the source
    sinb = (
        np.sin(dec_rad) * np.sin(con.dec_ngp_rad)
        + np.cos(dec_rad)
        * np.cos(ra_rad - con.ra_ngp_rad) * np.cos(con.dec_ngp_rad)
    )
    sinb = np.clip(sinb, -1.0, 1.0)  # Clip to handle numerical issues

    # Galactic latitude from -90 deg to 90 deg,
    # this is the default range of np.arcsin()
    gal_b = np.arcsin(sinb)

    # phi is an angle defined to calculate Galactic longitude
    sinphi = (
        (1 / np.cos(gal_b))
        * (
            - np.cos(dec_rad) * np.cos(ra_rad - con.ra_ngp_rad)
            * np.sin(con.dec_ngp_rad)
            + np.sin(dec_rad) * np.cos(con.dec_ngp_rad)
        )
    )

    cosphi = (
        (1 / np.cos(gal_b)) * np.cos(dec_rad) * np.sin(ra_rad - con.ra_ngp_rad)
    )

    # np.atan2 function can handle the sign, the result is between -pi and pi
    # to convert negative angle to positive angle, add 2 * pi
    phi = np.arctan2(sinphi, cosphi) + 2 * np.pi

    gal_lon = phi + (con.theta_ngp_rad - np.pi / 2)

    # This is to wrap the angle at 2pi or 360 degree.
    gal_lon = gal_lon % (2 * np.pi)

    l_deg = np.degrees(gal_lon)  # convert to degree
    b_deg = np.degrees(gal_b)  # convert to degree

    return (
        l_deg.item() if l_deg.size == 1 else l_deg,
        b_deg.item() if b_deg.size == 1 else b_deg,
    )
