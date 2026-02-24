"""
Different models for distance estimation from parallax.
"""
import numpy as np
from scipy.stats import truncnorm


class SimpleInversion:
    """
    Distance model object by inverting parallaxing.
    """

    def __init__(self, parallax: float, parallax_error: float):
        if parallax <= 0:
            raise ValueError(
                    "To use SimpleInversion, parallax must be positive."
            )

        if parallax_error <= 0:
            raise ValueError(
                    "parallax_error must be a positive number."
            )

        self.parallax = parallax
        self.parallax_error = parallax_error

    @property
    def d_est(self) -> float:
        return 1.0 / self.parallax

    @property
    def d_est_error(self) -> float:
        return self.parallax_error / (self.parallax ** 2)

    @property
    def parallax_over_error(self) -> float:
        return self.parallax / self.parallax_error

    def sample_distance(
            self, n_samples: int = 1000, dist_lo: float = 0,
            dist_up: float = np.inf
    ) -> np.ndarray:
        """
        A sampler that samples random distance based on a truncated normal
        distribution centred on the inversion of parallax with a standard
        deviation equal to parallax_error / parallax^2.

        Parameters
        ----------
        n_samples : int, optional
            Number of random samples to generate, by default 1000

        dist_lo : float, optional
            Lower bound for distance sampling, by default 0. Should keep it
            default.

        dist_up : float, optional
            Upper bound for distance sampling, by default np.inf. Should
            keep it default.

        Returns
        -------
        np.ndarray
            Array of sampled random distances.

        Raises
        ------
        ValueError
            If n_samples is not a positive integer.

        TypeError
            If n_samples is not an integer.
        """

        if not isinstance(n_samples, int):
            raise TypeError("n_samples must be an integer.")

        if isinstance(n_samples, int) and n_samples <= 0:
            raise ValueError("n_samples must be a positive integer.")

        # Generate samples from truncated normal distribution
        a = (dist_lo - self.d_est) / self.d_est_error
        b = (dist_up - self.d_est) / self.d_est_error

        samples = (
            truncnorm.rvs(a=a, b=b, size=n_samples) * self.d_est_error
            + self.d_est
        )

        return samples
