import pytest
from cobtools.astrometry.rotation_curve import get_rotation_curve
from cobtools import constants as con
from pathlib import Path
import numpy as np
import tempfile


class TestGetRotationCurve:
    def test_returns_callable(self):
        """Test that get_rotation_curve returns a callable function."""
        rot_curve = get_rotation_curve()
        assert callable(rot_curve)

    def test_invalid_r_sun_raises_error(self):
        """Test that non-positive r_sun raises ValueError."""
        with pytest.raises(
            ValueError, match="r_sun and theta_sun must be positive"
        ):
            get_rotation_curve(r_sun=-1.0)

        with pytest.raises(
            ValueError, match="r_sun and theta_sun must be positive"
        ):
            get_rotation_curve(r_sun=0.0)

    def test_invalid_theta_sun_raises_error(self):
        """Test that non-positive theta_sun raises ValueError."""
        with pytest.raises(
            ValueError, match="r_sun and theta_sun must be positive"
        ):
            get_rotation_curve(theta_sun=-1.0)

        with pytest.raises(
            ValueError, match="r_sun and theta_sun must be positive"
        ):
            get_rotation_curve(theta_sun=0.0)

    def test_missing_data_file_raises_error(self):
        """Test that missing data file raises FileNotFoundError."""
        with pytest.raises(
            FileNotFoundError, match="Rotation curve data not found"
        ):
            get_rotation_curve(data_path=Path("./nonexistent/path.npy"))

    def test_invalid_data_file_raises_error(self):
        """Test that invalid data file raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as f:
            f.write(b"invalid data")
            temp_path = Path(f.name)

        try:
            with pytest.raises(
                ValueError, match="Error loading rotation curve data"
            ):
                get_rotation_curve(data_path=temp_path)
        finally:
            temp_path.unlink()

    def test_clamping_negative_radii(self):
        """Test that negative radii are clamped to zero."""
        rot_curve = get_rotation_curve()
        v_at_zero = rot_curve(0.0)
        v_at_negative = rot_curve(-5.0)
        assert v_at_negative == v_at_zero

    def test_positive_radii_values(self):
        """
        Test that rotation curve returns positive velocity for positive radii.
        """
        rot_curve = get_rotation_curve()
        v = rot_curve(con.r_sun)
        assert v > 0
        assert np.isclose(v, con.theta_sun)

    def test_vectorized_input(self):
        """Test that rotation curve works with array input."""
        rot_curve = get_rotation_curve()
        radii = np.array([0.0, con.r_sun, 2 * con.r_sun])
        velocities = rot_curve(radii)
        assert len(velocities) == len(radii)
        assert all(v > 0 for v in velocities)
