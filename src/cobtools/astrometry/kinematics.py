"""
kinematics.py
=============

This module provides a suite of functions for computing Galactic space
velocities, including galactocentric 3D Cartesian velocities and peculiar
velocities. The formulation is based on the work of Reid et al. 2009.

Functions
---------

- **equatorial_to_galactic**: Convert equatorial coordinates (RA, Dec) to
  Galactic coordinates (l, b).

- **galactic_proper_motion**: Convert equatorial proper motions to Galactic
  proper motions.

- **galactocentric_cartesian_velocity**: Calculate galactocentric Cartesian
  velocities (u, v, w) and total space velocities (square root of the
  quadrature sum of u, v, w) from equatorial coordinates, proper motions,
  distance, and radial velocity.

- **peculiar_velocity**: Calculate the peculiar velocity and its Cartesian
  components by subtracting the local Galactic rotation.
"""
import numpy as np
import cobtools.constants as con
from cobtools.astrometry.rotation_curve import get_rotation_curve
from typing import Tuple, Union
from numpy.typing import ArrayLike


def equatorial_to_galactic(
        ra: Union[float, ArrayLike], dec: Union[float, ArrayLike]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert equatorial coordinates (ra, dec) to galactic coordinates
    (gal_l, gal_b).

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
        If ra and dec have different shapes, or if ra is not in [0,
        360) degrees, or if dec is not in [-90, 90] degrees.

    Example
    -------
    >>> from cobtools.astrometry.kinematics import equatorial_to_galactic
    >>> ra = 10.684  # degrees
    >>> dec = 41.269  # degrees
    >>> l, b = equatorial_to_galactic(ra, dec)
    >>> print(f"Galactic coordinates: l={l:.2f}, b={b:.2f} degrees")
    """

    ra = np.array(ra, ndmin=1)
    dec = np.array(dec, ndmin=1)

    if np.shape(ra) != np.shape(dec):
        raise ValueError("ra and dec must have the same shape.")

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
) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    """
    Calculate galactic proper motion (mu_l, mu_b) from equatorial proper motion
    (pmra_cosdec, pmdec) and equatorial coordinates (ra, dec).

    The basic idea is to calculate differences in ra and dec due to proper
    motion and convert it changes in Galactic coordinate.

    ra and dec should be in degrees, and their proper motion components should
    be in units of mas/yr; note that mu_ra_cosdec contain the cos(dec) factor.
    Input timestep should be in unit of years (default is 1).

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
        Time step in years for which to calculate the proper motion,
        by default 1.0.

    Returns
    -------
    Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]
        Proper motion in Galactic longitude (mu_l) and latitude (mu_b) in
        mas/yr. Note that mu_l does not contain the cos(b) factor,
        i.e., it is the proper motion in the direction of increasing Galactic
        longitude.

    Raises
    ------
    ValueError
        If the time step dt is not positive.

    Example
    -------
    >>> from cobtools.astrometry.kinematics import galactic_proper_motion
    >>> ra = 10.684  # degrees
    >>> dec = 41.269  # degrees
    >>> pmra_cosdec = 0.1  # mas/yr
    >>> pmdec = 0.2  # mas/yr
    >>> mu_l, mu_b = galactic_proper_motion(ra, dec, pmra_cosdec, pmdec)
    >>> print(f"Galactic proper motion: {mu_l:.2f}, {mu_b:.2f} mas/yr")
    """

    if dt <= 0:
        raise ValueError("Time step dt must be positive.")

    ra = np.array(ra)
    dec = np.array(dec)
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


def galactocentric_cartesian_velocity(
        ra: Union[float, ArrayLike], dec: Union[float, ArrayLike],
        pmra_cosdec: Union[float, ArrayLike], pmdec: Union[float, ArrayLike],
        dist: Union[float, ArrayLike], rv: Union[float, ArrayLike],
        u_sun: Union[float, ArrayLike] = con.u_sun,
        v_sun: Union[float, ArrayLike] = con.v_sun,
        w_sun: Union[float, ArrayLike] = con.w_sun,
        theta_sun: Union[float, ArrayLike] = con.theta_sun,
        dt: float = 1.0
):
    """
    Calculate Galactocentric Cartesian velocity components (u1, v1, w1) and
    the total space velocity (vspace) from equatorial coordinates,
    proper motions, distance, and radial velocity.

    Parameters
    ----------
    ra : float or ArrayLike
        Right ascension in decimal degrees.
    dec : float or ArrayLike
        Declination in decimal degrees.
    pmra_cosdec : float or ArrayLike
        Proper motion in ra*cos(dec), in mas/yr.
    pmdec : float or ArrayLike
        Proper motion in declination, in mas/yr.
    dist : float or ArrayLike
        Distance in kpc.
    rv : float or ArrayLike
        Radial velocity in km/s.
    u_sun : float or ArrayLike, optional
        Solar motion u component in km/s.
    v_sun : float or ArrayLike, optional
        Solar motion v component in km/s.
    w_sun : float or ArrayLike, optional
        Solar motion w component in km/s.
    theta_sun : float or ArrayLike, optional
        Solar rotation velocity in the Galactic plane in km/s.
    dt : float, optional
        Time step in years for which to calculate the proper motion,
        see `galactic_proper_motion`, by default 1.0 (year).

    Returns
    -------
    Tuple[Union[float, np.ndarray], Union[float, np.ndarray],
    Union[float, np.ndarray], Union[float, np.ndarray]]
        Galactocentric Cartesian velocities (u1, v1, w1, vspace) in km/s.

    Raises
    ------
    ValueError
        If ra is not in [0, 360) degrees, or if dec is not in [-90, 90]
        degrees.
    ValueError
        If dt is not a positive number.

    Example
    -------
    >>> from cobtools.astrometry.kinematics import \
    ... galactocentric_cartesian_velocity

    >>> ra = 10.684  # degrees
    >>> dec = 41.269  # degrees
    >>> pmra_cosdec = 0.1  # mas/yr
    >>> pmdec = 0.2  # mas/yr
    >>> dist = 0.77  # kpc
    >>> rv = -300  # km/s
    >>> u1, v1, w1, vspace = galactocentric_cartesian_velocity(
    ...     ra, dec, pmra_cosdec, pmdec, dist, rv
    ... )
    """

    ra = np.array(ra)
    dec = np.array(dec)
    pmra_cosdec = np.array(pmra_cosdec)
    pmdec = np.array(pmdec)
    dist = np.array(dist)
    rv = np.array(rv)
    u_sun = np.array(u_sun)
    v_sun = np.array(v_sun)
    w_sun = np.array(w_sun)
    theta_sun = np.array(theta_sun)

    gal_l, gal_b = equatorial_to_galactic(ra, dec)
    gal_l, gal_b = np.radians(gal_l), np.radians(gal_b)

    mu_l, mu_b = galactic_proper_motion(ra, dec, pmra_cosdec, pmdec, dt=dt)

    # Velocity components in the Galactic coordinate system (l, b)
    v_b = dist * mu_b * con.kpc_mas_per_yr_to_km_per_s
    v_l = dist * mu_l * np.cos(gal_b) * con.kpc_mas_per_yr_to_km_per_s

    # Convert the spherical coordinate to Galactic Cartesian coordinates at
    # the location of the Sun
    u1 = (
        (rv * np.cos(gal_b) - v_b * np.sin(gal_b))
        * np.cos(gal_l) - v_l * np.sin(gal_l)
    )

    v1 = (
        (rv * np.cos(gal_b) - v_b * np.sin(gal_b))
        * np.sin(gal_l) + v_l * np.cos(gal_l)
    )

    w1 = v_b * np.cos(gal_b) + rv * np.sin(gal_b)

    u2 = u1 + u_sun
    v2 = v1 + v_sun + theta_sun
    w2 = w1 + w_sun

    vspace = np.sqrt(u2**2 + v2**2 + w2**2)

    return u2, v2, w2, vspace


def peculiar_velocity(
        ra: Union[float, ArrayLike], dec: Union[float, ArrayLike],
        pmra_cosdec: Union[float, ArrayLike], pmdec: Union[float, ArrayLike],
        dist: Union[float, ArrayLike], rv: Union[float, ArrayLike],
        u_sun: Union[float, ArrayLike] = con.u_sun,
        v_sun: Union[float, ArrayLike] = con.v_sun,
        w_sun: Union[float, ArrayLike] = con.w_sun,
        theta_sun: Union[float, ArrayLike] = con.theta_sun,
        r_sun: Union[float, ArrayLike] = con.r_sun,
        dt: float = 1.0
) -> Tuple[
    Union[float, np.ndarray], Union[float, np.ndarray],
    Union[float, np.ndarray], Union[float, np.ndarray]
]:
    """
    Calculate the peculiar velocity and the cartesian components given its
    equatorial coordinates, proper motions, distance, and radial velocity.

    Parameters
    ----------
    ra : float or ArrayLike
        Right ascension in decimal degrees.
    dec : float or ArrayLike
        Declination in decimal degrees.
    pmra_cosdec : float or ArrayLike
        Proper motion in ra*cos(dec), in mas/yr.
    pmdec : float or ArrayLike
        Proper motion in declination, in mas/yr.
    dist : float or ArrayLike
        Distance in kpc.
    rv : float or ArrayLike
        Radial velocity in km/s.
    u_sun : float or ArrayLike, optional
        Solar motion u component in km/s.
    v_sun : float or ArrayLike, optional
        Solar motion v component in km/s.
    w_sun : float or ArrayLike, optional
        Solar motion w component in km/s.
    theta_sun : float or ArrayLike, optional
        Solar rotation velocity in the Galactic plane in km/s.
    r_sun : float or ArrayLike, optional
        Distance from the Sun to the Galactic center in kpc.
    dt : float, optional
        Time step in years for which to calculate the proper motion,
        see `galactic_proper_motion`, by default 1.0 (year).

    Returns
    -------
    Tuple[Union[float, np.ndarray], Union[float, np.ndarray],
    Union[float, np.ndarray], Union[float, np.ndarray]]
        Peculiar velocity components (u_s, v_s, w_s) and the total peculiar
        velocity (vpec) in km/s. Note that u_s is the component toward the
        Galactic center, v_s is the component in the direction of Galactic
        rotation, and w_s is the component toward the North Galactic Pole.

    Example
    -------
    >>> from cobtools.astrometry.kinematics import peculiar_velocity
    >>> import numpy as np
    >>> # Single value example
    >>> ra = 10.684  # degrees
    >>> dec = 41.269  # degrees
    >>> pmra_cosdec = 0.1  # mas/yr
    >>> pmdec = 0.2  # mas/yr
    >>> dist = 0.77  # kpc
    >>> rv = -300  # km/s
    >>> u_s, v_s, w_s, vpec = peculiar_velocity(
    ...     ra, dec, pmra_cosdec, pmdec, dist, rv
    ... )
    >>> # Array broadcasting example
    >>> ra_array = 10.684  # degrees
    >>> dec_array = 41.269  # degrees
    >>> pmra_cosdec_array = np.random.normal(-0.35, 0.08, 100)  # mas/yr
    >>> pmdec_array = np.random.normal(0.1, 0.05, 100)  # mas/yr
    >>> dist_array = np.random.normal(1.2, 0.3, 100) # kpc
    >>> rv_array = 15.0  # km/s
    >>> u_s_arr, v_s_arr, w_s_arr, vpec_arr = peculiar_velocity(
    ...     ra_array, dec_array, pmra_cosdec_array, pmdec_array,
    ...     dist_array, rv_array
    ... )
    """

    gal_l, gal_b = equatorial_to_galactic(ra, dec)
    gal_l, gal_b = np.radians(gal_l), np.radians(gal_b)

    u2, v2, w2, vspace = galactocentric_cartesian_velocity(
        ra, dec, pmra_cosdec, pmdec, dist, rv,
        u_sun=u_sun, v_sun=v_sun, w_sun=w_sun,
        theta_sun=theta_sun, dt=dt
    )

    d_p = dist * np.cos(gal_b)
    r_p = np.sqrt(r_sun ** 2 + d_p ** 2 - 2 * r_sun * d_p * np.cos(gal_l))

    vrot_interp = get_rotation_curve()
    vrot = vrot_interp(r_p)

    sinbeta = np.sin(gal_l) * (d_p / r_p)
    cosbeta = (r_sun - d_p * np.cos(gal_l)) / r_p

    u_s = u2 * cosbeta - v2 * sinbeta
    v_s = u2 * sinbeta + v2 * cosbeta - vrot
    w_s = w2

    vpec = np.sqrt(u_s ** 2 + v_s ** 2 + w_s ** 2)

    return u_s, v_s, w_s, vpec
