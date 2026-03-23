"""
A data model for light curves.

Classes
-------
LightCurve
    A data class representing a light curve, which consists of time-series
    data for flux measurements and their associated uncertainties. The class
    includes methods for rebinning the light curve into fixed time intervals
    and for folding the light curve on a specified period.
"""

from dataclasses import dataclass
import numpy as np
from numpy.typing import ArrayLike


@dataclass
class LightCurve:
    """
    A data class representing a light curve.

    Parameters
    ----------
    time_axis : ArrayLike
        An array of time values in an appropriate time unit (e.g., MJD, JD,
        seconds).

    flux : ArrayLike
        Fluxes corresponding to the time axis.

    flux_err : ArrayLike
        The corresponding uncertainties on the fluxes.

    Attributes
    ----------
    time_axis : numpy.ndarray
        An array of time values in an appropriate time unit (e.g., MJD, JD,
        seconds).

    flux : numpy.ndarray
        Fluxes corresponding to the time axis.

    flux_err : numpy.ndarray
        The corresponding uncertainties on the fluxes.

    Methods
    -------
    rebin(bin_size: float)
        Rebin light curve into time bins of fixed intervals (even binning).
        This method modifies the light curve in place.

    fold(period: float) -> "LightCurve"
        Fold the light curve on a given period and return a new LightCurve
        instance with the folded data.
    """
    time_axis: ArrayLike
    flux: ArrayLike
    flux_err: ArrayLike

    def __post_init__(self):
        if not isinstance(self.time_axis, np.ndarray):
            object.__setattr__(self, 'time_axis', np.array(self.time_axis))
        if not isinstance(self.flux, np.ndarray):
            object.__setattr__(self, 'flux', np.array(self.flux))
        if not isinstance(self.flux_err, np.ndarray):
            object.__setattr__(self, 'flux_err', np.array(self.flux_err))

    def rebin(self, bin_size: float):
        """
        Regroup light curve data into bins of fixed time intervals.

        Parameters
        ----------
            bin_size (float): Size of each time bin. The unit should be the
            same as that of the time_axis. If None, no rebinning is performed.

        Returns
        -------
            binned_time (numpy.ndarray): Midpoints of the time bins.
            binned_flux (numpy.ndarray): Average flux in each bin.
            binned_flux_err (numpy.ndarray): Average flux error in each bin.
        """
        if bin_size is None:
            return

        # Create bins
        bins = np.arange(
            self.time_axis.min(), self.time_axis.max() + bin_size, bin_size
        )
        bin_indices = np.digitize(self.time_axis, bins) - 1

        # Calculate binned time and flux
        binned_time = []
        binned_flux = []
        binned_flux_err = []
        for i in range(len(bins) - 1):
            mask = bin_indices == i
            if np.any(mask):
                binned_time.append((bins[i] + bins[i + 1]) / 2)
                binned_flux.append(np.mean(self.flux[mask]))
                binned_flux_err.append(
                    np.sqrt(
                        np.sum(self.flux_err[mask] ** 2)
                        / len(self.flux[mask])
                    )
                )

        self.time_axis = np.array(binned_time)
        self.flux = np.array(binned_flux)
        self.flux_err = np.array(binned_flux_err)

    def fold(self, period: float) -> "LightCurve":
        """
        Fold the light curve on a given period.

        Parameters
        ----------
            period (float): The period to fold the light curve on. The unit
            should be the same as that of the time_axis.

        Returns
        -------
            folded_time (numpy.ndarray): Time values folded on the period.
            folded_flux (numpy.ndarray): Corresponding flux values.
            folded_flux_err (numpy.ndarray): Corresponding flux error values.
        """
        t0 = self.time_axis.min()
        phase = ((self.time_axis - t0) % period) / period

        sorted_indices = np.argsort(phase)
        return LightCurve(
            time_axis=phase[sorted_indices],
            flux=self.flux[sorted_indices],
            flux_err=self.flux_err[sorted_indices]
        )
