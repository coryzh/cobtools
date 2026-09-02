import click
import numpy as np
from cobtools.astrometry.kinematics import peculiar_velocity


def calc_vpec(
        ra: float, dec: float, pmra: float, pmdec: float,
        distance: float, rv: float, conf: float, n_samples: int
) -> None:
    pass


def display_results(vpec_sample: np.ndarray, conf: float) -> None:
    pass


if __name__ == "__main__":
    calc_vpec()
