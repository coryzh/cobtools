"""
Compute normalised rotation curve using galpy
"""
import numpy as np
from galpy.potential import calcRotcurve, MWPotential2014
from importlib import resources


def generate_vrot_grid(step_size: float = 0.01) -> None:
    r_grid = np.arange(step_size, 3 + step_size, step_size)

    v_rot = calcRotcurve(
        MWPotential2014, Rs=r_grid
    )

    rot_curve_data = np.column_stack((r_grid, v_rot))
    out_path = resources.files("cobtools.data") / "rotcurve_mw2014.npy"
    np.save(out_path, rot_curve_data)


if __name__ == "__main__":
    generate_vrot_grid()
