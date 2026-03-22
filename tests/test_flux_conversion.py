import pytest
from cobtools.photometry.flux_conversion import magnitude_to_flux
from cobtools.data_models.band import Band
import numpy as np


class TestMagnitudeToFlux:
    @pytest.fixture
    def band(self):
        """Create a fixture Band instance for testing."""
        mock_band = Band("gaia_g")
        return mock_band

    def test_magnitude_to_flux_scalar(self, band):
        """Test conversion with a scalar magnitude."""
        result = magnitude_to_flux(10.0, band)
        assert np.isscalar(result)
        assert isinstance(result, float)
        assert np.isfinite(result)

    def test_magnitude_to_flux_array(self, band):
        """Test conversion with an array of magnitudes."""
        mags = np.array([10.0, 15.0, 20.0])
        result = magnitude_to_flux(mags, band)
        assert isinstance(result, np.ndarray)
        assert result.shape == mags.shape
        assert np.all(np.isfinite(result))

    def test_magnitude_to_flux_list(self, band):
        """Test conversion with a list of magnitudes."""
        mags = [10.0, 15.0, 20.0]
        result = magnitude_to_flux(mags, band)
        assert isinstance(result, np.ndarray)
        assert len(result) == len(mags)

    def test_magnitude_to_flux_invalid_mag_type(self, band):
        """Test that invalid magnitude type raises ValueError."""
        with pytest.raises(
            ValueError, match="mag must be a float or array-like"
        ):
            magnitude_to_flux("invalid", band)

    def test_magnitude_to_flux_multidimensional_array(self, band):
        """Test that multidimensional array raises ValueError."""
        mags = np.array([[10.0, 15.0], [20.0, 25.0]])
        with pytest.raises(
            ValueError, match="mag must be a scalar or 1D array"
        ):
            magnitude_to_flux(mags, band)

    def test_magnitude_to_flux_non_finite_values(self, band):
        """Test that non-finite values raise ValueError."""
        with pytest.raises(
            ValueError, match="mag must contain finite values"
        ):
            magnitude_to_flux(np.array([10.0, np.inf, 20.0]), band)

    def test_magnitude_to_flux_invalid_band_type(self):
        """Test that invalid band type raises TypeError."""
        with pytest.raises(
            TypeError, match="band must be an instance of Band"
        ):
            magnitude_to_flux(10.0, "not_a_band")
