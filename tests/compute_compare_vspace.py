import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from cobtools.astrometry.kinematics import (
    galactocentric_cartesian_velocity, equatorial_to_galactic
)
from astropy.coordinates import SkyCoord, Galactocentric, CartesianDifferential
from astropy.units import Unit
from cobtools import constants as con


def test_find_discrepancies(threshold=0, n_sample=1000, random_seed=42):
    """Generate random astrometric parameters and find discrepancies."""
    np.random.seed(random_seed)
    ra = np.random.uniform(0, 360, n_sample)
    dec = np.random.uniform(-90, 90, n_sample)
    pmra_cosdec = np.random.uniform(-5, 5, n_sample)
    pmdec = np.random.uniform(-5, 5, n_sample)
    dist = np.random.uniform(0.1, 5, n_sample)
    rv = np.random.uniform(-100, 100, n_sample)

    v_sun = CartesianDifferential(
        con.u_sun * Unit("km/s"),
        (con.v_sun + con.theta_sun) * Unit("km/s"),
        con.w_sun * Unit("km/s")
    )

    gc_frame = Galactocentric(
        galcen_distance=con.r_sun * Unit("kpc"),
        galcen_v_sun=v_sun,
        z_sun=0 * Unit("pc")
    )

    coords = SkyCoord(
        ra=ra * Unit("deg"),
        dec=dec * Unit("deg"),
        distance=dist * Unit("kpc"),
        pm_ra_cosdec=pmra_cosdec * Unit("mas/yr"),
        pm_dec=pmdec * Unit("mas/yr"),
        radial_velocity=rv * Unit("km/s"),
        frame="icrs"
    )

    coords_gc = coords.transform_to(gc_frame)
    coords_gc.representation_type = "cartesian"

    u_astropy = coords_gc.v_x.to("km/s").value
    v_astropy = coords_gc.v_y.to("km/s").value
    w_astropy = coords_gc.v_z.to("km/s").value
    v_space_astropy = np.sqrt(u_astropy**2 + v_astropy**2 + w_astropy**2)
    l, b = equatorial_to_galactic(ra, dec)
    u, v, w, vspace = galactocentric_cartesian_velocity(
        ra=ra, dec=dec, pmra_cosdec=pmra_cosdec,
        pmdec=pmdec, dist=dist, rv=rv, dt=0.01
    )

    discrepancies = []
    for i in range(n_sample):
        discrepancies.append(
            {
                "ra": ra[i],
                "dec": dec[i],
                "pmra_cosdec": pmra_cosdec[i],
                "pmdec": pmdec[i],
                "dist": dist[i],
                "rv": rv[i],
                "u_cobtools": u[i],
                "u_astropy": u_astropy[i],
                "v_cobtools": v[i],
                "v_astropy": v_astropy[i],
                "w_cobtools": w[i],
                "w_astropy": w_astropy[i],
                "vspace_cobtools": vspace[i],
                "vspace_astropy": v_space_astropy[i],
                "l": l[i],
                "b": b[i]
            }
        )

    df_comparison = pd.DataFrame(data=discrepancies)
    out_file = Path("data/vspace_comparison.csv")
    if not out_file.parent.exists():
        out_file.parent.mkdir(parents=True, exist_ok=True)

    df_comparison.to_csv(out_file, index=False)

    return df_comparison


def plot_comparison(df_comparison: pd.DataFrame) -> None:
    fig, ax = plt.subplots(2, 2, figsize=(12, 12))

    df_comparison.plot(
        x="u_astropy", y="u_cobtools", kind="scatter", ax=ax[0, 0], alpha=0.5
    )
    df_comparison.plot(
        x="v_astropy", y="v_cobtools", kind="scatter", ax=ax[0, 1], alpha=0.5
    )
    df_comparison.plot(
        x="w_astropy", y="w_cobtools", kind="scatter", ax=ax[1, 0], alpha=0.5
    )
    df_comparison.plot(
        x="vspace_astropy", y="vspace_cobtools",
        kind="scatter", ax=ax[1, 1], alpha=0.5
    )

    out_file = Path("figures/vspace_comparison.pdf")
    for i in range(2):
        for j in range(2):
            col_name = ['u', 'v', 'w', 'vspace'][j]
            astropy_col = f"{col_name}_astropy"
            min_val = df_comparison[astropy_col].min()
            max_val = df_comparison[astropy_col].max()
            ax[i, j].plot(
                [min_val, max_val],
                [min_val, max_val],
                color="red",
                linestyle="--"
            )

            ax[i, j].set_xlim(min_val, max_val)
            ax[i, j].set_ylim(min_val, max_val)

    if not out_file.parent.exists():
        out_file.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(out_file, bbox_inches="tight")


if __name__ == "__main__":
    df_comparison = test_find_discrepancies()
    plot_comparison(df_comparison)
