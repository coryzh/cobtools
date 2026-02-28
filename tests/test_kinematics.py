import pytest
import numpy as np
import pandas as pd
import cobtools.constants as con
from cobtools.astrometry.kinematics import (
    equatorial_to_galactic, galactic_proper_motion,
    galactocentric_cartesian_velocity
)
from astropy.coordinates import SkyCoord, Galactocentric, CartesianDifferential
from astropy.units import Unit


class TestEquatorialToGalactic:
    def test_invalid_ra_input(self):
        with pytest.raises(ValueError):
            equatorial_to_galactic(ra=-10.3, dec=10.5)

    def test_invalid_dec_input(self):
        with pytest.raises(ValueError):
            equatorial_to_galactic(ra=10.3, dec=100.5)

    def test_valid_single_number_input(self):
        ra, dec = 103.1, 89.3
        coord = SkyCoord(ra=ra, dec=dec, unit='deg', frame='icrs')
        gal_l, gal_b = equatorial_to_galactic(ra, dec)
        l_astropy, b_astropy = coord.galactic.l.deg, coord.galactic.b.deg
        assert isinstance(gal_l, float) and isinstance(gal_b, float)
        assert np.isclose(gal_l, l_astropy)
        assert np.isclose(gal_b, b_astropy)

    def test_valid_list_input(self):
        ra = [10.3, 150.3, 355.1]
        dec = [5.3, 25.1, 88.2]
        gal_l, gal_b = equatorial_to_galactic(ra, dec)
        coord = SkyCoord(ra=ra, dec=dec, unit='deg', frame='icrs')
        l_astropy, b_astropy = coord.galactic.l.deg, coord.galactic.b.deg
        print(gal_l, gal_b)
        assert isinstance(gal_l, np.ndarray) and isinstance(gal_b, np.ndarray)
        assert gal_l.shape == (len(ra),) and gal_b.shape == (len(dec),)
        assert np.allclose(gal_l, l_astropy)
        assert np.allclose(gal_b, b_astropy)

    def test_compare_to_astropy(self):
        n_sample = 10000
        np.random.seed(42)
        ra = np.random.uniform(0, 360, size=n_sample)
        dec = np.random.uniform(-90, 90, size=n_sample)
        gal_l, gal_b = equatorial_to_galactic(ra, dec)
        coord = SkyCoord(ra=ra, dec=dec, unit='deg', frame='icrs')
        l_astropy, b_astropy = coord.galactic.l.deg, coord.galactic.b.deg
        assert np.allclose(gal_l, l_astropy, atol=5e-3)
        assert np.allclose(gal_b, b_astropy, atol=5e-3)

    def test_compare_to_astropy_from_file(self):
        """
        Compare pre-computed results loaded from a data file.
        """
        df = pd.read_csv("data/vspace_discrepancy.csv")
        ra = df['ra'].values
        dec = df['dec'].values
        gal_l, gal_b = equatorial_to_galactic(ra, dec)
        coord = SkyCoord(ra=ra, dec=dec, unit='deg', frame='icrs')
        l_astropy, b_astropy = coord.galactic.l.deg, coord.galactic.b.deg
        assert np.allclose(gal_l, l_astropy, atol=1e-3)
        assert np.allclose(gal_b, b_astropy, atol=1e-3)

    def test_egdge_cases(self):
        ra = con.ra_ngp_deg
        dec = con.dec_ngp_deg

        _, gal_b = equatorial_to_galactic(ra, dec)
        assert np.allclose(gal_b, 90.0)


class TestGalacticProperMotion:
    def test_invalid_dt(self):
        with pytest.raises(ValueError):
            galactic_proper_motion(
                ra=10.3, dec=5.3, pmra_cosdec=15.2, pmdec=-20.1, dt=-1
            )

    def test_valid_single_input(self):
        ra, dec = 103.1, 89.3
        pmra_cosdec, pmdec = 15.2, -20.1
        mu_l, mu_b = galactic_proper_motion(ra, dec, pmra_cosdec, pmdec)
        coord = SkyCoord(
            ra=ra * Unit("deg"), dec=dec * Unit("deg"),
            pm_ra_cosdec=pmra_cosdec * Unit("mas/yr"),
            pm_dec=pmdec * Unit("mas/yr"),
            frame='icrs'
        )
        mu_b_astropy = coord.galactic.pm_b.to(Unit("mas/yr")).value
        mu_l_astropy = (
            coord.galactic.pm_l_cosb / np.cos(coord.galactic.b.radian)
        ).to(Unit("mas/yr")).value
        print(
            f"My results: mu_l={mu_l:.3f} mas/yr, mu_b={mu_b:.3f} mas/yr; "
            f"Astropy results: mu_l={mu_l_astropy:.3f} mas/yr, "
            f"mu_b={mu_b_astropy:.3f} mas/yr"
        )
        assert isinstance(mu_l, float) and isinstance(mu_b, float)
        assert np.isclose(mu_l, mu_l_astropy, atol=1e-3)
        assert np.isclose(mu_b, mu_b_astropy, atol=1e-3)

    def test_valid_list_input(self):
        ra = [10.3, 150.3, 355.1]
        dec = [5.3, 25.1, 88.2]
        pmra_cosdec = [15.2, -20.1, 5.5]
        pmdec = [-10.5, 30.2, -5.0]
        mu_l, mu_b = galactic_proper_motion(ra, dec, pmra_cosdec, pmdec)

        assert isinstance(mu_l, np.ndarray) and isinstance(mu_b, np.ndarray)
        assert mu_l.shape == (len(ra),) and mu_b.shape == (len(dec),)

    def test_valid_array_input(self):
        n_sample = 100000
        np.random.seed(42)
        ra = np.random.uniform(0, 360, size=n_sample)
        dec = np.random.uniform(-90, 90, size=n_sample)
        pmra_cosdec = np.random.uniform(-5, 5, size=n_sample)
        pmdec = np.random.uniform(-5, 5, size=n_sample)

        mu_l, mu_b = galactic_proper_motion(ra, dec, pmra_cosdec, pmdec)
        coord = SkyCoord(
            ra=ra * Unit("deg"), dec=dec * Unit("deg"),
            pm_ra_cosdec=pmra_cosdec * Unit("mas/yr"),
            pm_dec=pmdec * Unit("mas/yr"),
            frame='icrs'
        )
        mu_b_astropy = coord.galactic.pm_b.to(Unit("mas/yr")).value
        mu_l_astropy = (
            coord.galactic.pm_l_cosb / np.cos(coord.galactic.b.radian)
        ).to(Unit("mas/yr")).value

        if not (
            (np.allclose(mu_l, mu_l_astropy, rtol=1e-3)
             and np.allclose(mu_b, mu_b_astropy, rtol=1e-3))
        ):
            mismatch_indices = np.where(
                ~(
                    np.isclose(mu_l, mu_l_astropy, atol=1e-2)
                    & np.isclose(mu_b, mu_b_astropy, atol=1e-2)
                )
            )[0]

            print(f"Number of mismatches: {len(mismatch_indices)}")
            print("Sample mismatches:")
            for idx in mismatch_indices[:10]:  # Print first 10 mismatches
                print(
                    f"{idx}: ({ra[idx]:.2f}, {dec[idx]:.2f}, "
                    f"{pmra_cosdec[idx]:.2f}, {pmdec[idx]:.2f}), "
                    f"My: ({mu_l[idx]:.3f}, {mu_b[idx]:.3f}) mas/yr, "
                    f"Astropy: ({mu_l_astropy[idx]:.3f}, "
                    f"{mu_b_astropy[idx]:.3f}) mas/yr"
                )

        assert isinstance(mu_l, np.ndarray) and isinstance(mu_b, np.ndarray)
        assert mu_l.shape == (n_sample,) and mu_b.shape == (n_sample,)
        assert np.allclose(mu_l, mu_l_astropy, atol=5)
        assert np.allclose(mu_b, mu_b_astropy, atol=5)


class TestGalactocentricCartesianVelocity:
    """Unit tests for galactocentric_cartesian_velocity function."""

    def test_single_values(self):
        """Test with single velocity component values."""
        u, v, w, vspace = galactocentric_cartesian_velocity(
            ra=101.28715535, dec=-16.71611586, pmra_cosdec=1.3, pmdec=2.5,
            dist=1.5, rv=-20.5
        )

        assert isinstance(u, (float, np.ndarray))
        assert isinstance(v, (float, np.ndarray))
        assert isinstance(w, (float, np.ndarray))
        assert isinstance(vspace, (float, np.ndarray))
        assert np.allclose(np.sqrt(u**2 + v**2 + w**2), vspace)

    def test_array_values(self):
        n_sample = 1000
        ra = np.random.uniform(0, 360, n_sample)
        dec = np.random.uniform(-90, 90, n_sample)
        pmra_cosdec = np.random.uniform(-5, 5, n_sample)
        pmdec = np.random.uniform(-5, 5, n_sample)
        dist = np.random.uniform(0.1, 5, n_sample)
        rv = np.random.uniform(-100, 100, n_sample)
        u, v, w, vspace = galactocentric_cartesian_velocity(
            ra=ra, dec=dec, pmra_cosdec=pmra_cosdec, pmdec=pmdec,
            dist=dist, rv=rv
        )
        assert isinstance(u, np.ndarray)
        assert isinstance(v, np.ndarray)
        assert isinstance(w, np.ndarray)
        assert isinstance(vspace, np.ndarray)
        assert u.shape == (n_sample,)
        assert v.shape == (n_sample,)
        assert w.shape == (n_sample,)
        assert vspace.shape == (n_sample,)
        assert np.allclose(np.sqrt(u**2 + v**2 + w**2), vspace)

    def test_broadcast_single_rv_but_array_astrometry(self):
        n_sample = 1000
        ra = np.random.uniform(0, 360, n_sample)
        dec = np.random.uniform(-90, 90, n_sample)
        pmra_cosdec = np.random.uniform(-5, 5, n_sample)
        pmdec = np.random.uniform(-5, 5, n_sample)
        dist = np.random.uniform(0.1, 5, n_sample)
        rv = -20.5
        u, v, w, vspace = galactocentric_cartesian_velocity(
            ra=ra, dec=dec, pmra_cosdec=pmra_cosdec, pmdec=pmdec,
            dist=dist, rv=rv
        )
        assert isinstance(u, np.ndarray)
        assert isinstance(v, np.ndarray)
        assert isinstance(w, np.ndarray)
        assert isinstance(vspace, np.ndarray)
        assert u.shape == (n_sample,)
        assert v.shape == (n_sample,)
        assert w.shape == (n_sample,)
        assert vspace.shape == (n_sample,)
        assert np.allclose(np.sqrt(u**2 + v**2 + w**2), vspace)

    def test_compare_with_astropy(self):
        n_sample = 1000
        np.random.seed(41)
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
        vspace_astropy = np.sqrt(u_astropy**2 + v_astropy**2 + w_astropy**2)

        u, v, w, vspace = galactocentric_cartesian_velocity(
            ra=ra, dec=dec, pmra_cosdec=pmra_cosdec,
            pmdec=pmdec, dist=dist, rv=rv
        )

        for i in range(n_sample):
            print(
                f"cobtools: ({u[i]:.2f}, {v[i]:.2f}, {w[i]:.2f}, "
                f"{vspace[i]:.2f})km/s"
            )

            print(
                f"astropy: ({u_astropy[i]:.2f}, {v_astropy[i]:.2f}, "
                f"{w_astropy[i]:.2f}, {vspace_astropy[i]:.2f}) km/s\n"
            )
        assert np.allclose(u, u_astropy, rtol=1e-1)
        assert np.allclose(v, v_astropy, rtol=1e-1)
        assert np.allclose(w, w_astropy, rtol=1e-1)
        assert np.allclose(vspace, vspace_astropy, rtol=1e-1)
