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

    # Handle numerical instability for cos(gal_b) near 0.
    cos_gal_b = np.cos(gal_b)
    small_cos_gal_b_mask = cos_gal_b < 1e-10

    sinphi = np.zeros_like(gal_b)
    cosphi = np.zeros_like(gal_b)
    valid_mask = ~small_cos_gal_b_mask

    # phi is an angle defined to calculate Galactic longitude
    sinphi[valid_mask] = (
        (1 / cos_gal_b[valid_mask])
        * (
            - np.cos(dec_rad[valid_mask])
            * np.cos(ra_rad[valid_mask] - con.ra_ngp_rad)
            * np.sin(con.dec_ngp_rad)
            + np.sin(dec_rad[valid_mask]) * np.cos(con.dec_ngp_rad)
        )
    )

    cosphi[valid_mask] = (
        (1 / cos_gal_b[valid_mask])
        * np.cos(dec_rad[valid_mask])
        * np.sin(ra_rad[valid_mask] - con.ra_ngp_rad)
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


def galactic_proper_motion(
        ra: Union[float, ArrayLike], dec: Union[float, ArrayLike],
        pmra_cosdec: Union[float, ArrayLike], pmdec: Union[float, ArrayLike],
        dt: float = 1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    This function calculate differences in ra and dec due to PM and convert it
    to Galactic coordinate. Input ra and dec should be in degrees.
    Input equatorial PMs should be in units of mas/yr; note that mu_ra_cosdec
    contain the cos(dec) factor. Input timestep should be in unit of years
    (default is 1).

    Parameters
    ----------
    ra : float or ArrayLike
        Right ascension in decimal degrees.

    dec : float or ArrayLike
        Declination in decimal degrees.

    pmra_cosdec : float or ArrayLike
        Proper motion in right ascension multiplied by cos(dec), in mas/yr.

    pmdec : float or ArrayLike
        Proper motion in declination, in mas/yr.

    dt : float, optional
        Time step in arbitrary units for which to calculate the proper motion,
        by default 1.0.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Proper motion in Galactic longitude (mu_l) and latitude (mu_b) in
        mas/yr. Note that mu_l does not contain the cos(b) factor,
        i.e., it is the proper motion in the direction of increasing Galactic
        longitude.

    Raises
    ------
    ValueError
        If the time step dt is not positive.
    """

    if dt <= 0:
        raise ValueError("Time step dt must be positive.")

    pmra_cosdec = np.array(pmra_cosdec)
    pmdec = np.array(pmdec)

    # Compute differences in ra and dec (in degrees)
    cos_dec = np.cos(dec * (np.pi / 180.))
    dra = dt * (pmra_cosdec / cos_dec)
    ddec = dt * pmdec

    mas_to_deg = 1e-3 * (1 / 3600)  # conversion factor from mas to degree

    dra *= mas_to_deg
    ddec *= mas_to_deg

    # Then, apply the differences to the equatorial coordinates
    ra_new = ra + dra
    dec_new = dec + ddec

    gal_l_old, gal_b_old = equatorial_to_galactic(ra, dec)
    gal_l_new, gal_b_new = equatorial_to_galactic(ra_new, dec_new)

    # Calculate the differences in Galactic coordinates, taking care of the
    # wrap-around for longitude. E.g., if gal_l_old is 359.9 and gal_l_new
    # is 0.1, the difference should be 0.2, not -359.8.
    d_gal_l = (gal_l_new - gal_l_old + 180) % 360 - 180
    d_gal_b = gal_b_new - gal_b_old

    mu_l = d_gal_l / dt  # in degree/yr
    mu_b = d_gal_b / dt

    mu_l /= mas_to_deg
    mu_b /= mas_to_deg

    return mu_l, mu_b
