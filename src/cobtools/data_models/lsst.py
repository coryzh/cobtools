"""
Data models defined for the Vera C. Rubin Observatory's Legacy Survey of Space
and Time (LSST, hereafter) data. For more information, see the Rubin/LSST Alert
Product Data Schema [1]_.

Classes
-------
DiaSource
    A data class representing a single diaSource entry from the LSST product.
    A DiaSource (Difference Image Analysis Source) is a detection on a
    difference image.

DiaForcedSource
    A data class representing a single diaForcedSource entry from the LSST
    product.
    A DiaForcedSource is a forced photometry measurement at the a known
    position on a difference image.

DiaObject
    A data class representing a single diaObject entry from the LSST product.
    A DiaObject is a cataloged astrophysical object that has been identified as
    variable or transient based on time-series analysis of difference images.

Reference
---------
.. [1] Rubin/LSST Alert Product Data Schema:
    https://sdm-schemas.lsst.io/
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DiaSource:
    """
    Data class representing a single diaSource entry from the LSST product.

    A DiaSource (Difference Image Analysis Source) is a single detection on a
    difference image.

    Parameters
    ----------
    diaSourceId : int, optional
        Unique identifier for the diaSource record. Defaults to None.

    midpointMjdTai : float, optional
        Midpoint of the exposure in Modified Julian Date, in the TAI time
        standard. Defaults to None.

    band : str, optional
        Photometric band of the observation. Defaults to None.

    psfFlux : float, optional
        PSF-fit flux measured for the source on the difference image.
        Defaults to None.

    psfFluxErr : float, optional
        Uncertainty on the PSF-fit flux measurement. Defaults to None.

    reliability : float, optional
        Reliability score associated with the detection. Defaults to None.

    Attributes
    ----------
    diaSourceId : int or None
        Unique identifier for the diaSource record.

    midpointMjdTai : float or None
        Midpoint of the exposure in Modified Julian Date, in the TAI time
        standard.

    band : str or None
        Photometric band of the observation.

    psfFlux : float or None
        PSF-fit flux measured for the source on the difference image.

    psfFluxErr : float or None
        Uncertainty on the PSF-fit flux measurement.

    reliability : float or None
        Reliability score associated with the detection.
    """

    diaSourceId: Optional[int] = field(default=None)
    midpointMjdTai: Optional[float] = field(default=None)
    band: Optional[str] = field(default=None)
    psfFlux: Optional[float] = field(default=None)
    psfFluxErr: Optional[float] = field(default=None)
    reliability: Optional[float] = field(default=None)


@dataclass
class DiaForcedSource:
    """
    Data class representing a single diaForcedSource entry from the LSST
    product.

    Parameters
    ----------
    midpointMjdTai : float, optional
        Midpoint of the exposure in Modified Julian Date, in the TAI time
        standard. Defaults to None.

    band : str, optional
        Photometric band of the observation. Defaults to None.

    psfFlux : float, optional
        PSF-fit flux measured for the source on the difference image.
        Defaults to None.

    psfFluxErr : float, optional
        Uncertainty on the PSF-fit flux measurement. Defaults to None.

    Attributes
    ----------
    midpointMjdTai : float or None
        Midpoint of the exposure in Modified Julian Date, in the TAI time
        standard.

    band : str or None
        Photometric band of the observation.

    psfFlux : float or None
        PSF-fit flux measured for the source on the difference image.

    psfFluxErr : float or None
        Uncertainty on the PSF-fit flux measurement.
    """

    midpointMjdTai: Optional[float] = field(default=None)
    band: Optional[str] = field(default=None)
    psfFlux: Optional[float] = field(default=None)
    psfFluxErr: Optional[float] = field(default=None)


@dataclass
class DiaObject:
    """
    Data class representing a single diaObject entry from the LSST product.

    Parameters
    ----------
    diaObjectId : int, optional
        Unique identifier for the diaObject record.

    ra : float, optional
        Right Ascension of the object in degrees. Defaults to None.

    decl : float, optional
        Declination of the object in degrees. Defaults to None.

    firstDiaSourceMjdTai : float, optional
        Modified Julian Date (TAI) of the first associated diaSource detection.
        Defaults to None.

    lastDiaSourceMjdTai : float, optional
        Modified Julian Date (TAI) of the last associated diaSource detection.
        Defaults to None.

    Attributes
    ----------
    diaObjectId : int or None
        Unique identifier for the diaObject record.

    ra : float or None
        Right Ascension of the object in degrees.

    decl : float or None
        Declination of the object in degrees.

    firstDiaSourceMjdTai : float or None
        Modified Julian Date (TAI) of the first associated diaSource detection.

    lastDiaSourceMjdTai : float or None
        Modified Julian Date (TAI) of the last associated diaSource detection.
    """

    diaObjectId: Optional[int] = field(default=None)
    ra: Optional[float] = field(default=None)
    decl: Optional[float] = field(default=None)
    firstDiaSourceMjdTai: Optional[float] = field(default=None)
    lastDiaSourceMjdTai: Optional[float] = field(default=None)
