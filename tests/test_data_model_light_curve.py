import pytest
import numpy as np
from cobtools.data_models.light_curve import LightCurve


class TestLightCurveInitialization:
    """Test LightCurve initialization and __post_init__ conversion."""

    def test_initialization_with_lists(self):
        """Test that LightCurve can be initialized with lists."""
        time = [1.0, 2.0, 3.0]
        flux = [10.0, 20.0, 30.0]
        flux_err = [1.0, 2.0, 3.0]

        lc = LightCurve(time_axis=time, flux=flux, flux_err=flux_err)

        assert isinstance(lc.time_axis, np.ndarray)
        assert isinstance(lc.flux, np.ndarray)
        assert isinstance(lc.flux_err, np.ndarray)

    def test_initialization_with_numpy_arrays(self):
        """Test that LightCurve can be initialized with numpy arrays."""
        time = np.array([1.0, 2.0, 3.0])
        flux = np.array([10.0, 20.0, 30.0])
        flux_err = np.array([1.0, 2.0, 3.0])

        lc = LightCurve(time_axis=time, flux=flux, flux_err=flux_err)

        assert isinstance(lc.time_axis, np.ndarray)
        assert isinstance(lc.flux, np.ndarray)
        assert isinstance(lc.flux_err, np.ndarray)

    def test_arrays_converted_to_numpy(self):
        """Test that list inputs are properly converted to numpy arrays."""
        time = [1.0, 2.0, 3.0]
        flux = [10.0, 20.0, 30.0]
        flux_err = [1.0, 2.0, 3.0]

        lc = LightCurve(time_axis=time, flux=flux, flux_err=flux_err)

        np.testing.assert_array_equal(lc.time_axis, np.array(time))
        np.testing.assert_array_equal(lc.flux, np.array(flux))
        np.testing.assert_array_equal(lc.flux_err, np.array(flux_err))

    def test_single_element(self):
        """Test initialization with single element."""
        lc = LightCurve(time_axis=[1.0], flux=[10.0], flux_err=[1.0])

        assert len(lc.time_axis) == 1
        assert lc.time_axis[0] == 1.0
        assert lc.flux[0] == 10.0
        assert lc.flux_err[0] == 1.0

    def test_mismatched_lengths(self):
        """
            Test that initialization with mismatched lengths raises ValueError.
        """
        with pytest.raises(
            ValueError, match=(
                "time_axis, flux, and flux_err must have the same length."
            )
        ):
            LightCurve(time_axis=[1.0, 2.0], flux=[10.0], flux_err=[1.0, 2.0])

    def test_empty_time_axis(self):
        """
            Test that initialization with empty time_axis raises ValueError.
        """
        with pytest.raises(
            ValueError,
            match="Light curve must contain at least one data point."
        ):
            LightCurve(time_axis=[], flux=[], flux_err=[])


class TestLightCurveRebin:
    """Test the rebin method of LightCurve."""

    @pytest.fixture
    def sample_light_curve(self):
        """Create a sample light curve for testing."""
        # Create data with 100 points from time 0 to 10
        time = np.linspace(0, 10, 100)
        flux = np.sin(time) + 10  # Simple sinusoidal flux
        flux_err = np.ones(100) * 0.5
        return LightCurve(time_axis=time, flux=flux, flux_err=flux_err)

    def test_rebin_basic(self, sample_light_curve):
        """Test basic rebinning functionality."""
        lc = sample_light_curve
        original_flux = lc.flux.copy()

        lc.rebin(bin_size=2.0)

        # After binning, we should have fewer points
        assert len(lc.time_axis) < len(original_flux)
        # Time axis should contain bin midpoints
        assert np.all(np.diff(lc.time_axis) > 0)  # Monotonically increasing

    def test_rebin_none_bin_size(self, sample_light_curve):
        """Test that rebin with None returns None."""
        lc = sample_light_curve
        result = lc.rebin(bin_size=None)

        assert result is None

    def test_rebin_single_bin(self, sample_light_curve):
        """Test rebinning into a single large bin."""
        lc = sample_light_curve
        original_mean_flux = np.mean(lc.flux)

        lc.rebin(bin_size=100)  # Much larger than time range

        # Should have at least 1 bin with data
        assert len(lc.time_axis) >= 1
        # The binned flux should be close to the original mean
        assert np.allclose(lc.flux[0], original_mean_flux, rtol=0.1)

    def test_rebin_averages_flux(self):
        """Test that rebinning correctly averages flux values."""
        time = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5])
        flux = np.array([10.0, 12.0, 14.0, 16.0, 18.0, 20.0])
        flux_err = np.ones(6) * 0.5

        lc = LightCurve(time_axis=time, flux=flux, flux_err=flux_err)
        lc.rebin(bin_size=1.0)

        # Check that we have the expected rebinned values
        # Bin [0, 1): points at 0.0, 0.5 -> mean = (10 + 12) / 2 = 11
        # Bin [1, 2): points at 1.0, 1.5 -> mean = (14 + 16) / 2 = 15
        # Bin [2, 3): points at 2.0, 2.5 -> mean = (18 + 20) / 2 = 19
        expected_flux = np.array([11.0, 15.0, 19.0])
        np.testing.assert_allclose(lc.flux, expected_flux)

    def test_rebin_error_propagation(self):
        """Test that flux errors are properly propagated during rebinning."""
        time = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
        flux = np.array([10.0, 12.0, 14.0, 16.0, 18.0])
        flux_err = np.array([1.0, 1.5, 1.0, 1.5, 1.0])

        lc = LightCurve(time_axis=time, flux=flux, flux_err=flux_err)
        lc.rebin(bin_size=1.0)

        # All flux errors should be positive
        assert np.all(lc.flux_err > 0)
        # Flux errors should generally be smaller after rebinning
        # (more samples averaged)
        assert np.max(lc.flux_err) <= np.max(flux_err)

    def test_rebin_small_bin_size(self):
        """Test rebinning with small bin size."""
        time = np.linspace(0, 10, 50)
        flux = np.ones(50) * 10
        flux_err = np.ones(50)

        lc = LightCurve(time_axis=time, flux=flux, flux_err=flux_err)

        lc.rebin(bin_size=0.1)

        # With small bins, we may have fewer points than original
        # because not all bins may contain data
        assert len(lc.time_axis) > 0
        # But flux should still be approximately constant
        assert np.allclose(lc.flux, 10.0, rtol=0.01)


class TestLightCurveFold:
    """Test the fold method of LightCurve."""

    @pytest.fixture
    def sample_periodic_light_curve(self):
        """Create a periodic light curve for testing."""
        # Create a periodic light curve with period = 2.0
        time = np.linspace(0, 10, 200)
        flux = np.sin(2 * np.pi * time / 2.0) + 10  # Period = 2.0
        flux_err = np.ones(200) * 0.1
        return LightCurve(time_axis=time, flux=flux, flux_err=flux_err)

    def test_fold_basic(self, sample_periodic_light_curve):
        """Test basic folding functionality."""
        lc = sample_periodic_light_curve
        folded = lc.fold(period=2.0)

        # Should be a LightCurve instance
        assert isinstance(folded, LightCurve)
        # Should have same length as original
        assert len(folded.time_axis) == len(lc.time_axis)

    def test_fold_phase_range(self, sample_periodic_light_curve):
        """Test that folded time (phase) is in [0, 1]."""
        lc = sample_periodic_light_curve
        folded = lc.fold(period=2.0)

        assert np.all(folded.time_axis >= 0)
        assert np.all(folded.time_axis <= 1)

    def test_fold_preserves_flux(self, sample_periodic_light_curve):
        """Test that folding preserves flux and flux_err arrays."""
        lc = sample_periodic_light_curve
        original_flux = lc.flux.copy()
        original_flux_err = lc.flux_err.copy()

        folded = lc.fold(period=2.0)

        # Flux values should be preserved (possibly in different order).
        # Compare sorted arrays to ignore ordering while preserving
        # multiplicities.
        assert np.allclose(
            np.sort(folded.flux),
            np.sort(original_flux),
            rtol=0,
            atol=1e-10,
        )
        assert np.allclose(
            np.sort(folded.flux_err),
            np.sort(original_flux_err),
            rtol=0,
            atol=1e-10,
        )

    def test_fold_sorted_by_phase(self, sample_periodic_light_curve):
        """Test that folded light curve is sorted by phase."""
        lc = sample_periodic_light_curve
        folded = lc.fold(period=2.0)

        # The folded time axis should be monotonically increasing
        assert np.all(np.diff(folded.time_axis) >= 0)

    def test_fold_different_periods(self, sample_periodic_light_curve):
        """Test folding with different periods."""
        lc = sample_periodic_light_curve

        folded_1 = lc.fold(period=1.0)
        folded_2 = lc.fold(period=2.0)
        folded_4 = lc.fold(period=4.0)

        # All should be valid LightCurve objects
        assert isinstance(folded_1, LightCurve)
        assert isinstance(folded_2, LightCurve)
        assert isinstance(folded_4, LightCurve)

        # All should have phase in [0, 1]
        assert (
            np.all(folded_1.time_axis >= 0) and np.all(folded_1.time_axis <= 1)
        )
        assert (
            np.all(folded_2.time_axis >= 0) and np.all(folded_2.time_axis <= 1)
        )
        assert (
            np.all(folded_4.time_axis >= 0) and np.all(folded_4.time_axis <= 1)
        )

    def test_fold_single_period(self):
        """Test folding data that spans exactly one period."""
        time = np.linspace(0, 2.0, 100)
        flux = np.sin(2 * np.pi * time / 2.0) + 10
        flux_err = np.ones(100) * 0.1

        lc = LightCurve(time_axis=time, flux=flux, flux_err=flux_err)
        folded = lc.fold(period=2.0)

        # Phase should range from ~0 to 1
        assert np.min(folded.time_axis) >= 0
        assert np.max(folded.time_axis) <= 1

    def test_fold_preserves_length(self, sample_periodic_light_curve):
        """Test that folding doesn't change the number of data points."""
        lc = sample_periodic_light_curve
        original_length = len(lc.time_axis)

        folded = lc.fold(period=2.0)

        assert len(folded.time_axis) == original_length
        assert len(folded.flux) == original_length
        assert len(folded.flux_err) == original_length

    def test_fold_large_period(self, sample_periodic_light_curve):
        """Test folding with a period larger than the time span."""
        lc = sample_periodic_light_curve
        folded = lc.fold(period=100.0)  # Much larger than time range (0-10)

        # All phases should be less than 1
        assert np.all(folded.time_axis < 1)


class TestLightCurveIntegration:
    """Integration tests for multiple LightCurve operations."""

    def test_rebin_then_fold(self):
        """Test rebinning followed by folding."""
        time = np.linspace(0, 20, 500)
        flux = np.sin(2 * np.pi * time / 2.0) + 10
        flux_err = np.ones(500) * 0.1

        lc = LightCurve(time_axis=time, flux=flux, flux_err=flux_err)

        # First rebin
        lc.rebin(bin_size=0.5)
        rebinned_length = len(lc.time_axis)

        # Then fold
        folded = lc.fold(period=2.0)

        assert len(folded.time_axis) == rebinned_length
        assert np.all(folded.time_axis >= 0)
        assert np.all(folded.time_axis <= 1)

    def test_fold_creates_new_instance(self):
        """Test that fold returns a new instance without modifying original."""
        time = np.linspace(0, 10, 100)
        flux = np.sin(2 * np.pi * time / 2.0) + 10
        flux_err = np.ones(100) * 0.1

        lc = LightCurve(time_axis=time, flux=flux, flux_err=flux_err)
        original_time = lc.time_axis.copy()

        folded = lc.fold(period=2.0)

        # Original should be unchanged
        np.testing.assert_array_equal(lc.time_axis, original_time)
        # Folded should be different
        assert not np.allclose(folded.time_axis, original_time)

    def test_rebin_modifies_in_place(self):
        """Test that rebin modifies the object in place."""
        time = np.linspace(0, 10, 100)
        flux = np.sin(2 * np.pi * time / 2.0) + 10
        flux_err = np.ones(100) * 0.1

        lc = LightCurve(time_axis=time, flux=flux, flux_err=flux_err)
        original_length = len(lc.time_axis)

        lc.rebin(bin_size=1.0)

        # Length should change
        assert len(lc.time_axis) < original_length
