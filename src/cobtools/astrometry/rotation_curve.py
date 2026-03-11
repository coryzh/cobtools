import numpy as np
from cobtools import constants as con
from pathlib import Path
from scipy.interpolate import interp1d
from importlib import resources


def get_rotation_curve(
        r_sun: float = con.r_sun, theta_sun: float = con.theta_sun,
        data_path: Path = None
) -> np.ndarray:
    """
    Load a pre-computed rotation curve, and return an interpolated function
    for the rotation velocity as a function of radius.

    Parameters
    ----------
    r_sun : float, optional
        Distance from the Sun to the Galactic center in kpc,
        by default con.r_sun

    theta_sun : float, optional
        Circular velocity at the Sun's position in km/s,
        by default con.theta_sun

    data_path : Path, optional
        Path to the rotation curve data file,
        by default Path("./data/rotcurve_mw2014.npy")

    Returns
    -------
    np.ndarray
        Interpolated rotation velocity as a function of radius.
        The function extrapolates beyond the provided data range, but clamps
        negative radii to zero, i.e., v_rot(r < 0) = v_rot(0).

    Raises
    ------
    ValueError
        If r_sun or theta_sun are not positive values.
    FileNotFoundError
        If the rotation curve data file is not found.
    ValueError
        If there is an error loading the rotation curve data.
    """

    if r_sun <= 0 or theta_sun <= 0:
        raise ValueError("r_sun and theta_sun must be positive values.")

    if data_path is None:
        data_path = Path(
            resources.files("cobtools.data") / "rotcurve_mw2014.npy"
        )

    if not data_path.exists():
        raise FileNotFoundError(
            f"Rotation curve data not found at {data_path}. "
            f"Please run the script to generate the data."
        )

    try:
        rot_data = np.load(data_path)
    except Exception as e:
        raise ValueError(
            f"Error loading rotation curve data from {data_path}: {e}"
        )

    r_grid, v_grid = rot_data[:, 0], rot_data[:, 1]

    r_grid = r_grid * r_sun
    v_grid = v_grid * theta_sun

    v_rot_interp = interp1d(
        r_grid, v_grid, kind='linear', fill_value='extrapolate',
        bounds_error=False
    )

    def clamped_interp(r):
        r = np.maximum(r, 0)
        return v_rot_interp(r)

    return clamped_interp
