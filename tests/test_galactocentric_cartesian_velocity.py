import pytest
import numpy as np
from cobtools.astrometry.kinematics import galactocentric_cartesian_velocity


class TestGalactocentricCartesianVelocity:
    """Unit tests for galactocentric_cartesian_velocity function."""

    def test_single_values(self):
        """Test with single velocity component values."""
        u, v, w, vspace = galactocentric_cartesian_velocity(
            ra=101.28715535, dec=-16.71611586, pmra_cosdec=1.3, pmdec=2.5,
            dist=1.5, rv=-20.5
        )

        assert isinstance(u, (float, np.ndarray))
        assert isinstance(v, (float, np.ndarray))
        assert isinstance(w, (float, np.ndarray))
        assert isinstance(vspace, (float, np.ndarray))
        assert np.allclose(np.sqrt(u**2 + v**2 + w**2), vspace)

    def test_array_values(self):
        n_sample = 1000
        ra = np.random.uniform(0, 360, n_sample)
        dec = np.random.uniform(-90, 90, n_sample)
        pmra_cosdec = np.random.uniform(-5, 5, n_sample)
        pmdec = np.random.uniform(-5, 5, n_sample)
        dist = np.random.uniform(0.1, 5, n_sample)
        rv = np.random.uniform(-100, 100, n_sample)
        u, v, w, vspace = galactocentric_cartesian_velocity(
            ra=ra, dec=dec, pmra_cosdec=pmra_cosdec, pmdec=pmdec,
            dist=dist, rv=rv
        )
        assert isinstance(u, np.ndarray)
        assert isinstance(v, np.ndarray)
        assert isinstance(w, np.ndarray)
        assert isinstance(vspace, np.ndarray)
        assert u.shape == (n_sample,)
        assert v.shape == (n_sample,)
        assert w.shape == (n_sample,)
        assert vspace.shape == (n_sample,)
        assert np.allclose(np.sqrt(u**2 + v**2 + w**2), vspace)

    def test_broadcast_single_rv_but_array_astrometry(self):
        n_sample = 1000
        ra = np.random.uniform(0, 360, n_sample)
        dec = np.random.uniform(-90, 90, n_sample)
        pmra_cosdec = np.random.uniform(-5, 5, n_sample)
        pmdec = np.random.uniform(-5, 5, n_sample)
        dist = np.random.uniform(0.1, 5, n_sample)
        rv = -20.5
        u, v, w, vspace = galactocentric_cartesian_velocity(
            ra=ra, dec=dec, pmra_cosdec=pmra_cosdec, pmdec=pmdec,
            dist=dist, rv=rv
        )
        assert isinstance(u, np.ndarray)
        assert isinstance(v, np.ndarray)
        assert isinstance(w, np.ndarray)
        assert isinstance(vspace, np.ndarray)
        assert u.shape == (n_sample,)
        assert v.shape == (n_sample,)
        assert w.shape == (n_sample,)
        assert vspace.shape == (n_sample,)
        assert np.allclose(np.sqrt(u**2 + v**2 + w**2), vspace)
