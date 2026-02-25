import cobtools.constants as con
import pytest
import numpy as np


def test_ngp_coordinates_conversion():
    """Test that NGP coordinates are consistent across formats."""
    assert con.ra_ngp_deg == pytest.approx(192.8595070833333, rel=1e-9)
    assert con.dec_ngp_deg == pytest.approx(27.128336944444445, rel=1e-9)


def test_ngp_radians_conversion():
    """Test that NGP coordinates in radians match degree conversions."""
    assert con.ra_ngp_rad == pytest.approx(
        np.radians(con.ra_ngp_deg), rel=1e-9
    )
    assert con.dec_ngp_rad == pytest.approx(
        np.radians(con.dec_ngp_deg), rel=1e-9
    )


def test_theta_ngp_conversion():
    """Test that theta_ngp in radians matches degree conversion."""
    assert con.theta_ngp_rad == pytest.approx(
        np.radians(con.theta_ngp_deg), rel=1e-9
    )


def test_solar_motion_values():
    """Test that solar motion constants have expected values."""
    assert con.u_sun == 10.7
    assert con.v_sun == 15.6
    assert con.w_sun == 8.9
    assert con.du_sun == 1.8
    assert con.dv_sun == 6.8
    assert con.dw_sun == 0.9


def test_rotation_constants():
    """Test galactic rotation and solar distance constants."""
    assert con.theta_sun == 240.0
    assert con.d_theta_sun == 8
    assert con.r_sun == 8.34
    assert con.d_r_sun == 0.16
