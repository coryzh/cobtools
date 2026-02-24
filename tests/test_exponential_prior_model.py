import pytest
import numpy as np
from cobtools.astrometry.distance import XRBExponentialPriorModel
from pathlib import Path


class TestXRBExponentialPriorModel:
    def test_initialization(self):
        """Test basic initialization of XRBExponentialPriorModel."""
        model = XRBExponentialPriorModel(0.5, 0.1)
        assert model is not None

    def test_valid_input_parameters(self):
        """Test initialization with custom parameters."""
        model = XRBExponentialPriorModel(
            parallax=0.6, parallax_error=0.05, scale_length=2.0
        )
        assert model.scale_length == 2.0
        assert model.parallax == 0.6
        assert model.parallax_error == 0.05
        assert model.parallax_over_error == 0.6 / 0.05

    def test_invalid_parallax_error(self):
        """Test that invalid parallax_error raises ValueError."""
        with pytest.raises(ValueError):
            XRBExponentialPriorModel(parallax=0.5, parallax_error=-0.1)

        with pytest.raises(ValueError):
            XRBExponentialPriorModel(parallax=0.5, parallax_error=0)

        with pytest.raises(ValueError):
            XRBExponentialPriorModel(
                parallax=0.5, parallax_error=0.1, scale_length=-1.0
            )

    def test_negative_parallax(self):
        """Test that negative parallax is handled correctly."""
        model = XRBExponentialPriorModel(parallax=-0.5, parallax_error=0.1)
        assert model.parallax == -0.5
        assert model.parallax_error == 0.1
        assert model.parallax_over_error == -0.5 / 0.1

    def test_sample_distance_positive_parallax(self):
        """Test that sample_distance returns reasonable values."""
        model = XRBExponentialPriorModel(parallax=0.5, parallax_error=0.1)
        samples = model.sample_distance(nwalkers=10, nsteps=500, burn_in=100)
        assert len(samples) == 10 * (500 - 100)
        assert np.all(samples > 0)  # Distances should all be positive

    def test_sample_distance_invalid_sampler_parameters(self):
        """Test that non-integer nwalkers and nsteps raise ValueError."""
        model = XRBExponentialPriorModel(parallax=0.5, parallax_error=0.1)

        with pytest.raises(ValueError):
            model.sample_distance(nwalkers=3.5, nsteps=500, burn_in=100)

        with pytest.raises(ValueError):
            model.sample_distance(nwalkers=10, nsteps=2000.5, burn_in=100)

        with pytest.raises(ValueError):
            model.sample_distance(nwalkers=10, nsteps=500, burn_in=-50)

        with pytest.raises(ValueError):
            model.sample_distance(nwalkers=10, nsteps=200, burn_in=201)

    def test_plot_distance_samples(self):
        """Test that distance samples can be plotted without errors."""
        import matplotlib.pyplot as plt

        model = XRBExponentialPriorModel(parallax=0.5, parallax_error=0.1)
        samples = model.sample_distance(nwalkers=10, nsteps=500, burn_in=100)

        _ = plt.hist(
            samples, bins=50, density=True, label=f"{len(samples)} samples"
        )

        plt.axvline(
            1 / model.parallax, color="red", linestyle="--", label="1/parallax"
        )
        plt.xlabel("Distance (kpc)")
        plt.ylabel("Probability Density")
        plt.text(
            0.5, 0.8,
            f"Parallax: {model.parallax} mas\n"
            f"Parallax Error: {model.parallax_error} mas\n"
            f"Scale Length: {model.scale_length} kpc",
            fontsize=10,
            transform=plt.gca().transAxes,
        )
        plt.legend()
        out_path = Path().cwd() / "test_exponential_distance_samples.pdf"
        plt.savefig(out_path, bbox_inches="tight")
        plt.close()
