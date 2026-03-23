from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import TypeVar, Generic

TObject = TypeVar("TObject")


@dataclass(frozen=True)
class BrokerAuth:
    username: str | None = None
    token: str | None = None
    password: str | None = None


@dataclass(frozen=True)
class BrokerCapabilities:
    object_lookup: bool = False
    lightcurve_retrieval: bool = False
    image_retrieval: bool = False


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

    Attributes
    ----------
    auth : BrokerAuth
        Authentication credentials for the broker.

    capabilities : BrokerCapabilities
        Capabilities of the broker, indicating what types of queries it
        supports.
    """
    capabilities: BrokerCapabilities = BrokerCapabilities()

    def __init__(self, auth: BrokerAuth, endpoint: str | None = None):
        self.auth = auth
        self.endpoint = endpoint

    @cached_property
    def client(self):
        return self._build_client()

    @abstractmethod
    def _build_client(self):
        """
        Create and validate the underlying SDK/session/client.
        """
        raise NotImplementedError
