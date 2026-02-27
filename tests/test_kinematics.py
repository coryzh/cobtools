import pytest
import numpy as np
import pandas as pd
import cobtools.constants as con
from cobtools.astrometry.kinematics import (
    equatorial_to_galactic, galactic_proper_motion
)
from astropy.coordinates import SkyCoord
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
        The data file contains astrometry parameters that lead to large
        discrepancies between my results and those from astropy.
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
        # assert np.allclose(mu_l, mu_l_astropy, atol=1e-3)
        # assert np.allclose(mu_b, mu_b_astropy, atol=1e-3)
