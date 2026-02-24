import pytest
import numpy as np
from cobtools.astrometry.distance import SimpleInversion


class TestSimpleInversion:
    """Unit tests for SimpleInversion class."""

    def test_initialization(self):
        """Test SimpleInversion initialization."""
        inv = SimpleInversion(0.5, 0.2)
        assert inv is not None

    def test_class_attributes(self):
        """Test basic inversion operation."""
        inv = SimpleInversion(0.5, 0.2)
        assert inv.parallax == 0.5
        assert inv.parallax_error == 0.2

    def test_negative_parallax(self):
        """Test initialization with negative parallax."""
        with pytest.raises(ValueError):
            SimpleInversion(-0.5, 0.2)

    def test_zero_parallax(self):
        """Test initialization with zero parallax."""
        with pytest.raises(ValueError):
            SimpleInversion(0, 0.2)

    def test_negative_parallax_error(self):
        """Test initialization with negative parallax error."""
        with pytest.raises(ValueError):
            SimpleInversion(0.5, -0.2)

    def test_invert_estimate(self):
        """Test inversion with single element."""
        inv = SimpleInversion(0.5, 0.2)
        d_expected = 2.0
        d_error_expected = 0.2 / (0.5 ** 2)
        assert inv.d_est == d_expected
        assert inv.d_est_error == d_error_expected
        assert inv.parallax_over_error == 0.5 / 0.2

    def test_sample_distance_valid_n_samples(self):
        """Test distance sampling with valid n_samples."""
        inv = SimpleInversion(0.5, 0.2)
        samples = inv.sample_distance(n_samples=100)
        assert len(samples) == 100
        assert np.all(samples >= 0)

    def test_sample_distance_invalid_n_samples(self):
        """Test distance sampling with invalid n_samples."""
        inv = SimpleInversion(0.5, 0.2)
        with pytest.raises(TypeError):
            inv.sample_distance(n_samples=100.0)
        with pytest.raises(ValueError):
            inv.sample_distance(n_samples=-10)
