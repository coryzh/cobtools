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

    Attributes
    ----------
    parallax : float
        The measured parallax in milliarcseconds (mas).
        Must be positive for this method
    parallax_error : float
        The error in the measured parallax in milliarcseconds (mas).
        Must be positive.

    Methods
    -------
    d_est : float
        The estimated distance in kiloparsecs (kpc) obtained by inverting the
        parallax, i.e., d_est = 1 / parallax.

    d_est_error : float
        The error in the estimated distance, calculated using error propagation
        from the parallax error, i.e.,
        d_est_error = parallax_error / parallax^2.

    parallax_over_error : float
        The signal-to-noise ratio of the parallax measurement, calculated as
        parallax / parallax_error.

    sample_distance : np.ndarray
        A method to sample random distances based on a truncated normal
        distribution centred on the inversion of parallax with a standard
        deviation equal to parallax_error / parallax^2.

    Example
    -------
    >>> from cobtools.astrometry.distance import SimpleInversion
    >>> model = SimpleInversion(parallax=0.5, parallax_error=0.1)
    >>> print(model.d_est)  # Estimated distance
    2.0
    >>> print(model.d_est_error)  # Error in the estimated distance
    0.4
    >>> print(model.parallax_over_error)  # Signal-to-noise ratio
    5.0
    """

    def __init__(self, parallax: float, parallax_error: float):
        """
        Initialize the SimpleInversion model with parallax and its error.

        Parameters
        ----------
        parallax : float
            The measured parallax in milliarcseconds (mas). Must be positive.
        parallax_error : float
            The uncertainty of the parallax measurement in mas, must also
            be positive.

        Raises
        ------
        ValueError
            If parallax is not positive.
        ValueError
            If parallax_error is not positive.
        """
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
        """
        Estimate distance by inverting the parallax.

        Returns
        -------
        float
            The estimated distance in kiloparsecs (kpc).
        """
        return 1.0 / self.parallax

    @property
    def d_est_error(self) -> float:
        """
        Estimate the error in the distance estimate.

        Returns
        -------
        float
            The error in the estimated distance.
        """
        return self.parallax_error / (self.parallax ** 2)

    @property
    def parallax_over_error(self) -> float:
        """
        Calculate the signal-to-noise ratio of the parallax measurement.

        Returns
        -------
        float
            The signal-to-noise ratio.
        """
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

        Example
        -------
        >>> from cobtools.astrometry.distance import SimpleInversion
        >>> model = SimpleInversion(parallax=0.5, parallax_error=0.1)
        >>> samples = model.sample_distance(n_samples=1000)  # Sample distances
        >>> print(samples)  # Array of sampled distances
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
    """
    A class for taking literature distance estimates and errors. The errors
    can be asymmetric. The class has a method to model the asymmetric errors
    with a gamma distribution, and then sample distances from the fitted
    distribution.

    Attributes
    ----------
    x_est : float
        The estimated distance from the literature.
    x_lo : float
        The lower limit of the distance estimate from the literature.
    x_hi : float
        The upper limit of the distance estimate from the literature.
    conf_level : float
        The confidence level associated with the distance estimate, by default
        0.68.

    Methods
    -------
    x_loerr : float
        The lower error, calculated as x_est - x_lo.
    x_uperr : float
        The upper error, calculated as x_hi - x_est.
    sigma_0 : float
        The averaged error, calculated as 0.5 * (x_loerr + x_uperr).
    fit_gamma : dict
        Fit the literature nominal values to a gamma distribution and
        return the parameters of the fitted distribution.
    sample_distance : np.ndarray
        Sample distance from the fitted gamma distribution.

    Example
    -------
    >>> from cobtools.astrometry.distance import FromLiterature
    >>> model = FromLiterature(x_est=5.0, x_lo=4.0, x_hi=6.0)
    >>> print(model.x_loerr)  # Lower error
    1.0
    >>> print(model.x_uperr)  # Upper error
    1.0
    """
    def __init__(
            self, x_est: float, x_lo: float, x_hi: float,
            conf_level: float = 0.68
    ):
        """
        Initialize the FromLiterature model with distance estimates and errors.

        Parameters
        ----------
        x_est : float
            The estimated distance from the literature.
        x_lo : float
            The lower limit of the distance estimate from the literature.
        x_hi : float
            The upper limit of the distance estimate from the literature.
        conf_level : float, optional
            The confidence level associated with the distance estimate,
            by default 0.68

        Raises
        ------
        ValueError
            If x_lo is not less than x_hi.
        ValueError
            If x_est is not between x_lo and x_hi.
        ValueError
            If conf_level is not between 0 and 1.
        """
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
        """
        Calculate the lower error of the distance estimate.
        Returns
        -------
        float
            The lower error of the distance estimate.
        """
        return self.x_est - self.x_lo

    @property
    def x_uperr(self) -> float:
        """
        Calculate the upper error of the distance estimate.

        Returns
        -------
        float
            The upper error of the distance estimate.
        """
        return self.x_hi - self.x_est

    @property
    def sigma_0(self) -> float:
        """
        Calculate the averaged error, which could be used as an initial guess
        for fitting a skewed distribution.
        """
        return 0.5 * (self.x_loerr + self.x_uperr)

    @property
    def _sigma_min(self) -> float:
        """
        The minimum error between the lower and upper errors, which could be
        used as the lower bound for fitting a skewed distribution.

        Returns
        -------
        float
            The minimum error between the lower and upper errors.
        """
        return min(self.x_loerr, self.x_uperr)

    def fit_gamma(self) -> dict:
        """
        Fit the asymmetric errors from the literature to a gamma distribution.
        The fitting is done by minimizing the difference between the confidence
        intervals of the fitted gamma distribution and the literature values.

        Fitting is performed using the scipy.optimize.minimize function, with
        the initial guess for the scale parameter (sigma_x) set to the
        averaged error (self.sigma_0).

        Returns
        -------
        dict
            A dictionary containing the parameters of the fitted gamma
            distribution, including 'alpha', 'theta', and the 'distribution'
            object itself.
        """

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
        """
        Sample distance from the fitted gamma distribution.

        Parameters
        ----------
        n_samples : int, optional
            Number of random samples to generate, by default 1000

        Returns
        -------
        np.ndarray
            Array of sampled random distances from the fitted gamma
            distribution.

        Example
        -------
        >>> from cobtools.astrometry.distance import FromLiterature
        >>> model = FromLiterature(x_est=5.0, x_lo=4.0, x_hi=6.0)
        >>> samples = model.sample_distance(n_samples=100
        >>> print(samples)
        """
        gamma_params = self.fit_gamma()
        x_gamma = gamma_params["distribution"]

        samples = x_gamma.rvs(size=n_samples)

        return samples


class XRBExponentialPriorModel:
    """
    A class representing distance estimation using a Bayesian method with an
    exponential prior representative for X-ray binaries. The prior formualted
    as
        p(d) ~ d^2 * exp(-d / scale_length),

    where scale_length is a parameter obtained from fitting to known X-ray
    binaries in the literature (Zhao, Y+23).

    The likelihood is a Gaussian likelihood centered on 1/d with a standard
    deviation equal to the parallax error.

    This method can be used for negative parallaxes and low signal-to-noise
    ratio parallaxes.

    Attributes
    ----------
    parallax : float
        The measured parallax in milliarcseconds (mas). Could be negative.
    parallax_error : float
        The uncertainty of the parallax measurement in milliarcseconds (mas).
    scale_length : float
        The scale length of the exponential prior in kiloparsecs (kpc).
    """

    def __init__(
            self, parallax: float,
            parallax_error: float, scale_length: float = 1.97
    ):
        """
        Initialize the XRBExponentialPriorModel with parallax, its error, and
        the scale length of the exponential prior.

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

        Example
        -------
        >>> from cobtools.astrometry.distance import XRBExponentialPriorModel
        >>> model = XRBExponentialPriorModel(parallax=0.5, parallax_error=0.1)
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
