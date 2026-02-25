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
        l, b = equatorial_to_galactic(ra, dec)
        l_astropy, b_astropy = coord.galactic.l.deg, coord.galactic.b.deg
        assert isinstance(l, float) and isinstance(b, float)
        assert np.isclose(l, l_astropy)
        assert np.isclose(b, b_astropy)

    def test_valid_list_input(self):
        ra = [10.3, 150.3, 355.1]
        dec = [5.3, 25.1, 88.2]
        l, b = equatorial_to_galactic(ra, dec)
        print(l, b)
        assert isinstance(l, np.ndarray) and isinstance(b, np.ndarray)
        assert l.shape == (len(ra),) and b.shape == (len(dec),)
