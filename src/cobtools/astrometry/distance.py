"""
This module provides various classes for estimating distances from parallax.

Classes
-------
- SimpleInversion: A simple model for distance estimation by inverting
parallax.
- FromLiterature: Fits literature values to a gamma distribution.
- XRBExponentialPriorModel: A Bayesian model using an exponential prior.

The module also includes methods for sampling distances and fitting
distributions.
"""
import numpy as np
from scipy.stats import truncnorm, gamma
from scipy.optimize import minimize, Bounds
from typing import Any
from functools import partial
import emcee


class SimpleInversion:
    """
    A class for estimating distance from parallax using simple inversion.
    Use this method when the measured parallax is positive and has a high
    signal-to-noise ratio. Commonly parallax/parallax_error >= 5 is preferred.
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


class FromLiterature:
    def __init__(
            self, x_est: float, x_lo: float, x_hi: float,
            conf_level: float = 0.68
    ):
        self.x_est = x_est
        self.x_lo = x_lo
        self.x_hi = x_hi
        self.conf_level = conf_level

        if x_lo >= x_hi:
            raise ValueError(
                "Lower limit (x_lo) must be less than the upper limit (x_hi)."
            )

        if x_est < x_lo or x_est > x_hi:
            raise ValueError(
                "Estimated value (x_est) must be between x_lo and x_hi."
            )

        if conf_level < 0 or conf_level > 1:
            raise ValueError(
                "Confidence level must be a number between 0 and 1."
            )

    @property
    def x_loerr(self) -> float:
        return self.x_est - self.x_lo

    @property
    def x_uperr(self) -> float:
        return self.x_hi - self.x_est

    @property
    def sigma_0(self) -> float:
        """
        Averaged error, which could be used as an initial guess for fitting
        a skewed distribution.
        """
        return 0.5 * (self.x_loerr + self.x_uperr)

    @property
    def _sigma_min(self) -> float:
        return min(self.x_loerr, self.x_uperr)

    def fit_gamma(self) -> dict:
        """Fit the literature nominal values to a gamma distribution."""

        def get_gamma_distribution(sigma_x) -> dict:
            alpha = (
                (
                    2 * sigma_x + self.x_est ** 2
                    + np.sqrt(4 * sigma_x * self.x_est ** 2 + self.x_est ** 4)
                )
                / (2 * sigma_x)
            )

            theta = self.x_est / (alpha - 1)
            x_gamma = gamma(a=alpha, scale=theta)

            return dict(alpha=alpha, theta=theta, distribution=x_gamma)

        def difference(sigma_x) -> float:
            _re = get_gamma_distribution(sigma_x)
            x_gamma = _re["distribution"]

            x_lo_model = x_gamma.ppf((1 - self.conf_level) / 2)
            x_hi_model = x_gamma.ppf((1 + self.conf_level) / 2)

            diff = np.sqrt(
                (self.x_lo - x_lo_model) ** 2 + (self.x_hi - x_hi_model) ** 2
            )

            return diff

        results = minimize(
            difference, x0=self.sigma_0, bounds=Bounds(self._sigma_min, np.inf)
        )

        return get_gamma_distribution(results.x[0])

    def sample_distance(
            self, n_samples: int = 1000
    ) -> np.ndarray:
        """Sample distance from the fitted gamma distribution."""
        gamma_params = self.fit_gamma()
        x_gamma = gamma_params["distribution"]

        samples = x_gamma.rvs(size=n_samples)

        return samples


class XRBExponentialPriorModel:
    """
    Distance Bayesian model based on a exponential prior derived from known
    X-ray binaries.
    """

    def __init__(
            self, parallax: float,
            parallax_error: float, scale_length: float = 1.97
    ):
        """
        A Bayesian distance model using an exponential prior. The exponential
        prior has a scale_length parameter obtained from fitting to known
        X-ray binaries in the literature.

        Parameters
        ----------
        parallax : float
            The measured parallax in milliarcseconds (mas). Could be negative.
        parallax_error : float
            The uncertainty of the parallax measurement in
            milliarcseconds (mas).
        scale_length : float, optional
            The scale length of the exponential prior in kiloparsecs (kpc),
            by default 1.97 (Zhao, Y+23)

        Raises
        ------
        ValueError
            If parallax_error is not a positive number.
        ValueError
            If scale_length is not a positive number.
        """

        if parallax_error <= 0:
            raise ValueError(
                "parallax_error must be a positive number."
            )

        if scale_length <= 0:
            raise ValueError(
                "scale_length must be a positive number."
            )

        self.parallax = parallax
        self.parallax_error = parallax_error
        self.scale_length = scale_length

    @property
    def parallax_over_error(self) -> float:
        return self.parallax / self.parallax_error

    def log_prior(self, d: float) -> float:
        if d < 0:
            return -np.inf

        else:
            return 2 * np.log(d) - d / self.scale_length

    def log_likelihood(self, d) -> float:
        if d < 0:
            return -np.inf

        else:
            return (
                -0.5 * (self.parallax - 1 / d) ** 2 / self.parallax_error ** 2
            )

    def log_posterior(self, d) -> float:
        return self.log_prior(d) + self.log_likelihood(d)

    def sample_distance(
            self, nwalkers: int = 4, nsteps: int = 2000, burn_in: int = 500,
            **kwargs: Any
    ) -> np.ndarray[Any, np.dtype[np.float64]]:
        """
        Sample the posterior distribution using the
        MCMC sampler in emcee.

        Parameters
        ----------
        nwalkers : int, optional
            Number of walkers for the MCMC sampler, by default 4
        nsteps : int, optional
            Number of steps for each walker, by default 2000
        burn_in : int, optional
            Number of steps to discard as burn-in, by default 500
        kwargs : Any
            Additional keyword arguments to pass to the emcee.EnsembleSampler

        Returns
        -------
        np.ndarray[Any, np.dtype[np.float64]]
            Array of sampled distances from the posterior distribution.
        """
        if not isinstance(nwalkers, int) or nwalkers <= 0:
            raise ValueError("nwalkers must be a positive integer.")

        if not isinstance(nsteps, int) or nsteps <= 0:
            raise ValueError("nsteps must be a positive integer.")

        if not isinstance(burn_in, int) or burn_in < 0:
            raise ValueError("burn_in must be a non-negative integer.")

        if burn_in >= nsteps:
            raise ValueError("burn_in must be less than nsteps.")

        initial_distances = np.random.uniform(0.1, 20, size=nwalkers)

        log_prob_fn = partial(self.log_posterior)
        sampler = emcee.EnsembleSampler(
            nwalkers=nwalkers, ndim=1, log_prob_fn=log_prob_fn, **kwargs
        )

        _ = sampler.run_mcmc(
            initial_distances[:, None], nsteps=nsteps, progress=False
        )

        samples = sampler.get_chain(discard=burn_in, flat=True)[:, 0]

        return samples
