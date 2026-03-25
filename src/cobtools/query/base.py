"""
Base layer for broker query clients, defining the interface and common
structures for interacting with different Rubin/LSST data brokers.

Classes
-------
BrokerAuth
    A data class representing authentication credentials for a broker.

BrokerCapabilities
    A data class representing the capabilities of a broker, such as whether it
    supports object lookup, light curve retrieval, and image retrieval.

BrokerError
    Base exception class for errors related to broker interactions.

BrokerAuthError
    Exception raised for authentication failures with the broker.

BrokerQueryError
    Exception raised for errors during query execution with the broker.

BrokerClient
    Abstract base class for a broker client providing a blueprint for wrappers
    around different Rubin/LSST data brokers. Subclasses should implement the
    _build_client method to create and validate the underlying
    SDK/session/client.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import TypeVar, Generic

TObject = TypeVar("TObject")


@dataclass(frozen=True)
class BrokerAuth:
    """
    Data class representing authentication credentials for a broker.

    Parameters
    ----------
    username : str, optional
        Username for authentication. Defaults to None.

    token : str, optional
        API token for authentication. Defaults to None.

    password : str, optional
        Password for authentication. Defaults to None.

    Attributes
    ----------
    username : str or None
        Username for authentication.

    token : str or None
        API token for authentication.

    password : str or None
        Password for authentication.
    """
    username: str | None = None
    token: str | None = None
    password: str | None = None


@dataclass(frozen=True)
class BrokerCapabilities:
    """
    Data class representing the capabilities of a broker.

    Parameters
    ----------
    object_lookup : bool, optional
        Whether the broker supports looking up objects by ID. Defaults to
        False.

    lightcurve_retrieval : bool, optional
        Whether the broker supports retrieving light curves. Defaults to False.

    image_retrieval : bool, optional
        Whether the broker supports retrieving images. Defaults to False.

    Attributes
    ----------
    object_lookup : bool
        Whether the broker supports looking up objects by ID.

    lightcurve_retrieval : bool
        Whether the broker supports retrieving light curves.

    image_retrieval : bool
        Whether the broker supports retrieving images.

    tap_service : bool
        Whether the broker supports TAP service.
    """
    object_lookup: bool = False
    lightcurve_retrieval: bool = False
    image_retrieval: bool = False
    tap_service: bool = False


class BrokerError(RuntimeError):
    """Base class for exceptions related to broker interactions."""
    pass


class BrokerAuthError(BrokerError):
    """Exception raised for authentication failures with the broker."""
    pass


class BrokerQueryError(BrokerError):
    """Exception raised for errors during query execution with the broker."""
    pass


class BrokerClient(ABC, Generic[TObject]):
    """
    Abstract base class for a broker client that can query for objects of type
    ``TObject``.

    Parameters
    ----------
    auth : BrokerAuth
        Authentication credentials for the broker.

    endpoint : str, optional
        Custom API endpoint for the broker. Defaults to None, in which case the
        client will use the default endpoint defined by the subclass.

    Attributes
    ----------
    auth : BrokerAuth
        Authentication credentials for the broker.

    endpoint : str or None
        Custom API endpoint for the broker.

    capabilities : BrokerCapabilities
        Capabilities of the broker, indicating what types of queries it
        supports.

    Methods
    -------
    _build_client()
        Abstract method that must be implemented by subclasses to create and
        validate the underlying SDK/session/client for interacting with the
        broker.

    client
        Cached property that returns the initialized client instance, built
        using the _build_client method.
    """

    capabilities: BrokerCapabilities = BrokerCapabilities()

    def __init__(self, auth: BrokerAuth, endpoint: str | None = None):
        self.auth = auth
        self.endpoint = endpoint

    @cached_property
    def client(self):
        """
        Client instance for interacting with the broker, initialized lazily on
        first access.
        """
        return self._build_client()

    @abstractmethod
    def _build_client(self):
        """
        Create and validate the underlying SDK/session/client.
        """
        raise NotImplementedError
