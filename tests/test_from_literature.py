import pytest
import numpy as np
from cobtools.astrometry.distance import FromLiterature


class TestFromLiterature:
    """Unit tests for the FromLiterature class."""

    def test_initialization(self):
        """Test that FromLiterature can be initialized."""
        fl = FromLiterature(6.5, 5.0, 8.0)
        assert fl is not None

    def test_literature_distance_valid_input(self):
        """Test getting distance for a valid source."""
        fl = FromLiterature(3.5, 1.8, 6.5)
        assert fl.x_est == 3.5
        assert fl.x_lo == 1.8
        assert fl.x_hi == 6.5
        assert fl.conf_level == 0.68
        assert fl.x_loerr == 3.5 - 1.8
        assert fl.x_uperr == 6.5 - 3.5
        assert fl.sigma_0 == 0.5 * ((3.5 - 1.8) + (6.5 - 3.5))

    def test_literature_distance_invalid_input(self):
        """Test that invalid input raises ValueError."""
        with pytest.raises(ValueError):
            FromLiterature(5.0, 6.0, 4.0)  # x_lo >= x_hi

        with pytest.raises(ValueError):
            FromLiterature(5.0, 4.0, 6.0, conf_level=-0.1)  # conf_level < 0

        with pytest.raises(ValueError):
            FromLiterature(5.0, 4.0, 6.0, conf_level=1.1)  # conf_level > 1

    def test_fit_gamma(self):
        """Test fitting a gamma distribution."""
        fl = FromLiterature(3.5, 1.8, 6.5)
        gamma_params = fl.fit_gamma()
        assert 'alpha' in gamma_params
        assert 'theta' in gamma_params
        assert 'distribution' in gamma_params

    def test_sample_distance(self):
        """Test sampling distances from the fitted gamma distribution."""
        fl = FromLiterature(3.5, 1.8, 6.5)
        gamma_params = fl.fit_gamma()
        x_gamma = gamma_params['distribution']
        samples = x_gamma.rvs(size=1000)
        assert len(samples) == 1000
        assert np.all(samples > 0)
