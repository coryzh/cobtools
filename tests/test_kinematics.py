import pytest
import numpy as np
from cobtools.astrometry.kinematics import equatorial_to_galactic
from astropy.coordinates import SkyCoord


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
