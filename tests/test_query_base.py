import pytest
from cobtools.query.base import (
    BrokerAuth,
    BrokerCapabilities,
    BrokerError,
    BrokerAuthError,
    BrokerQueryError,
    BrokerClient,
)


# ---------------------------------------------------------------------------
# BrokerAuth
# ---------------------------------------------------------------------------

class TestBrokerAuth:
    def test_defaults_are_none(self):
        auth = BrokerAuth()
        assert auth.token is None
        assert auth.username is None
        assert auth.password is None

    def test_token_only(self):
        auth = BrokerAuth(token="abc123")
        assert auth.token == "abc123"
        assert auth.username is None
        assert auth.password is None

    def test_all_fields(self):
        auth = BrokerAuth(username="user", token="tok", password="pw")
        assert auth.username == "user"
        assert auth.token == "tok"
        assert auth.password == "pw"

    def test_is_immutable(self):
        auth = BrokerAuth(token="tok")
        with pytest.raises(Exception):
            auth.token = "other"  # frozen dataclass must raise


# ---------------------------------------------------------------------------
# BrokerCapabilities
# ---------------------------------------------------------------------------

class TestBrokerCapabilities:
    def test_all_false_by_default(self):
        caps = BrokerCapabilities()
        assert caps.object_lookup is False
        assert caps.lightcurve_retrieval is False
        assert caps.image_retrieval is False

    def test_selective_flags(self):
        caps = BrokerCapabilities(
            object_lookup=True, lightcurve_retrieval=True
        )
        assert caps.object_lookup is True
        assert caps.lightcurve_retrieval is True
        assert caps.image_retrieval is False

    def test_all_true(self):
        caps = BrokerCapabilities(
            object_lookup=True,
            lightcurve_retrieval=True,
            image_retrieval=True,
        )
        assert caps.object_lookup is True
        assert caps.lightcurve_retrieval is True
        assert caps.image_retrieval is True

    def test_is_immutable(self):
        caps = BrokerCapabilities(object_lookup=True)
        with pytest.raises(Exception):
            caps.object_lookup = False


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------

class TestBrokerExceptions:
    def test_broker_error_is_runtime_error(self):
        assert issubclass(BrokerError, RuntimeError)

    def test_auth_error_is_broker_error(self):
        assert issubclass(BrokerAuthError, BrokerError)

    def test_query_error_is_broker_error(self):
        assert issubclass(BrokerQueryError, BrokerError)

    def test_auth_error_can_be_raised_and_caught_as_broker_error(self):
        with pytest.raises(BrokerError):
            raise BrokerAuthError("bad token")

    def test_query_error_can_be_raised_and_caught_as_broker_error(self):
        with pytest.raises(BrokerError):
            raise BrokerQueryError("query failed")

    def test_auth_error_message_preserved(self):
        with pytest.raises(BrokerAuthError, match="bad token"):
            raise BrokerAuthError("bad token")


# ---------------------------------------------------------------------------
# BrokerClient
# ---------------------------------------------------------------------------

class _StubClient(BrokerClient):
    """Minimal concrete subclass for testing."""
    capabilities = BrokerCapabilities(object_lookup=True)

    def _build_client(self):
        return object()


class _FailingClient(BrokerClient):
    """Subclass whose _build_client raises BrokerAuthError."""

    def _build_client(self):
        raise BrokerAuthError("no token")


class TestBrokerClient:
    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            BrokerClient(auth=BrokerAuth())  # type: ignore[abstract]

    def test_auth_stored(self):
        auth = BrokerAuth(token="tok")
        broker = _StubClient(auth=auth)
        assert broker.auth is auth

    def test_endpoint_stored(self):
        auth = BrokerAuth(token="tok")
        broker = _StubClient(auth=auth, endpoint="https://example.com/api")
        assert broker.endpoint == "https://example.com/api"

    def test_endpoint_defaults_to_none(self):
        broker = _StubClient(auth=BrokerAuth())
        assert broker.endpoint is None

    def test_capabilities_on_subclass(self):
        broker = _StubClient(auth=BrokerAuth())
        assert broker.capabilities.object_lookup is True
        assert broker.capabilities.lightcurve_retrieval is False
        assert broker.capabilities.image_retrieval is False

    def test_client_is_lazy(self):
        """_build_client should not be called at instantiation time."""
        build_called = []

        class _Tracked(BrokerClient):
            def _build_client(self):
                build_called.append(True)
                return object()

        _ = _Tracked(auth=BrokerAuth())
        assert build_called == [], "_build_client should not be called at init"

    def test_client_is_cached(self):
        """Accessing .client twice should return the same object."""
        broker = _StubClient(auth=BrokerAuth())
        first = broker.client
        second = broker.client
        assert first is second

    def test_build_client_called_once(self):
        call_count = []

        class _Counted(BrokerClient):
            def _build_client(self):
                call_count.append(1)
                return object()

        broker = _Counted(auth=BrokerAuth())
        _ = broker.client
        _ = broker.client
        assert sum(call_count) == 1

    def test_build_client_error_propagates(self):
        broker = _FailingClient(auth=BrokerAuth())
        with pytest.raises(BrokerAuthError, match="no token"):
            _ = broker.client
