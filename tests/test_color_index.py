import pytest
import numpy as np
from cobtools.photometry.color_index import bp_rp_to_teff


class TestBpRpToTeff:
    def test_bp_rp_to_teff_scalar_valid(self):
        # Typical valid input for 'dwarf'
        teff = bp_rp_to_teff(1.0, mh=-0.5, kind="dwarf")
        assert isinstance(teff, float)
        assert teff > 0

    def test_bp_rp_to_teff_array_valid(self):
        bp_rp = np.array([0.5, 1.0, 1.5])
        mh = np.array([0.0, -0.5, -1.0])
        teff = bp_rp_to_teff(bp_rp, mh=mh, kind="dwarf")
        assert isinstance(teff, np.ndarray)
        assert teff.shape == bp_rp.shape
        assert np.all(teff > 0)

    def test_bp_rp_to_teff_mh_broadcast(self):
        bp_rp = np.array([0.5, 1.0, 1.5])
        mh = -0.5  # Scalar mh should be broadcasted
        teff = bp_rp_to_teff(bp_rp, mh=mh, kind="dwarf")
        assert isinstance(teff, np.ndarray)
        assert teff.shape == bp_rp.shape
        assert np.all(teff > 0)

    def test_bp_rp_to_teff_default_mh(self):
        bp_rp = np.array([0.5, 1.0, 1.5])
        teff = bp_rp_to_teff(bp_rp, kind="dwarf")  # mh should default to 0
        assert isinstance(teff, np.ndarray)
        assert teff.shape == bp_rp.shape
        assert np.all(teff > 0)

    def test_bp_rp_to_teff_invalid_kind(self):
        with pytest.raises(ValueError):
            bp_rp_to_teff(1.0, kind="invalid_kind")

        with pytest.raises(TypeError):
            bp_rp_to_teff(1.0, kind=123)

    def test_bp_rp_to_teff_shape_mismatch(self):
        bp_rp = np.array([1.0, 1.5])
        mh = np.array([0.0])
        with pytest.raises(ValueError):
            bp_rp_to_teff(bp_rp, mh=mh, kind="dwarf")

    def test_bp_rp_to_teff_out_of_bounds(self):
        # Use a value outside the valid bp_rp range for 'dwarf'
        with pytest.raises(ValueError):
            bp_rp_to_teff(0.1, kind="dwarf")

        with pytest.raises(ValueError):
            bp_rp_to_teff(5.0, kind="dwarf")

        with pytest.raises(ValueError):
            bp_rp_to_teff(-0.5, kind="giant")

        with pytest.raises(ValueError):
            bp_rp_to_teff(3.0, kind="giant")

    def test_bp_rp_to_teff_non_convertible_input(self):
        with pytest.raises(
            TypeError,
            match="bp_rp must be convertible to a numpy array of float"
        ):
            bp_rp_to_teff("not_a_number", kind="dwarf")

        with pytest.raises(
            TypeError,
            match="mh must be convertible to a numpy array of float"
        ):
            bp_rp_to_teff(1.0, mh="not_a_number", kind="dwarf")
