"""
Unit tests for cobtools.query.query_lasair.LasairBrokerClient.

The lasair SDK client is mocked throughout so no real network calls are made.
"""
import copy
import json
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

from cobtools.query.base import BrokerAuth, BrokerAuthError, BrokerQueryError
from cobtools.query.query_lasair import LasairBrokerClient
from cobtools.data_models.lsst_lasair import LasairObject
from cobtools.data_models.light_curve import LightCurve


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def auth():
    return BrokerAuth(token="test-token")


@pytest.fixture
def auth_no_token():
    return BrokerAuth()


@pytest.fixture
def real_lasair_payload():
    file_path = Path(__file__).with_name("dia_source_data.json")
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _raw_api_dict():
    """Minimal raw API payload that LasairObject.from_api_data can parse."""
    return {
        "diaObjectId": 42,
        "lasairData": {},
        "diaObject": {"diaObjectId": 42, "ra": 10.0, "decl": -5.0},
        "diaSourcesList": [
            {
                "diaSourceId": 1,
                "midpointMjdTai": 60000.0,
                "band": "g",
                "psfFlux": 100.0,
                "psfFluxErr": 1.0,
                "reliability": None,
            }
        ],
        "diaForcedSourcesList": [],
    }


# ---------------------------------------------------------------------------
# Capabilities and defaults
# ---------------------------------------------------------------------------

class TestLasairBrokerClientCapabilities:
    def test_capabilities(self, auth):
        broker = LasairBrokerClient(auth=auth)
        assert broker.capabilities.object_lookup is True
        assert broker.capabilities.lightcurve_retrieval is True
        assert broker.capabilities.image_retrieval is False

    def test_default_endpoint_class_attribute(self):
        assert (
            LasairBrokerClient.DEFAULT_ENDPOINT
            == "https://api.lasair.lsst.ac.uk/api"
        )

    def test_endpoint_stored(self, auth):
        broker = LasairBrokerClient(auth=auth, endpoint="https://custom.api/")
        assert broker.endpoint == "https://custom.api/"


# ---------------------------------------------------------------------------
# _build_client / authentication
# ---------------------------------------------------------------------------

class TestBuildClient:
    def test_raises_auth_error_without_token(self, auth_no_token):
        broker = LasairBrokerClient(auth=auth_no_token)
        with pytest.raises(BrokerAuthError, match="token is required"):
            _ = broker.client

    def test_raises_auth_error_when_sdk_fails(self, auth):
        broker = LasairBrokerClient(auth=auth)
        with patch(
            "cobtools.query.query_lasair.lasair",
            side_effect=RuntimeError("connection refused"),
        ):
            with pytest.raises(
                BrokerAuthError, match="Failed to authenticate"
            ):
                _ = broker.client

    def test_returns_sdk_client_on_success(self, auth):
        mock_sdk = MagicMock()
        broker = LasairBrokerClient(auth=auth)
        with patch(
            "cobtools.query.query_lasair.lasair", return_value=mock_sdk
        ):
            assert broker.client is mock_sdk

    def test_passes_token_and_endpoint_to_sdk(self, auth):
        mock_lasair = MagicMock(return_value=MagicMock())
        broker = LasairBrokerClient(auth=auth)
        with patch("cobtools.query.query_lasair.lasair", mock_lasair):
            _ = broker.client
        mock_lasair.assert_called_once_with(
            token="test-token",
            endpoint=LasairBrokerClient.DEFAULT_ENDPOINT,
        )


# ---------------------------------------------------------------------------
# get_diaobject
# ---------------------------------------------------------------------------

class TestGetDiaobject:
    def test_returns_lasair_object(self, auth):
        mock_sdk = MagicMock()
        mock_sdk.object.return_value = _raw_api_dict()

        broker = LasairBrokerClient(auth=auth)
        with patch(
            "cobtools.query.query_lasair.lasair", return_value=mock_sdk
        ):
            result = broker.get_diaobject(42)

        assert isinstance(result, LasairObject)
        assert result.diaObjectId == 42

    def test_passes_kwargs_to_sdk(self, auth):
        mock_sdk = MagicMock()
        mock_sdk.object.return_value = _raw_api_dict()

        broker = LasairBrokerClient(auth=auth)
        with patch(
            "cobtools.query.query_lasair.lasair", return_value=mock_sdk
        ):
            broker.get_diaobject(42, lasair_added=True, lite=True)

        mock_sdk.object.assert_called_once_with(
            42, lasair_added=True, lite=True
        )

    def test_raises_query_error_on_sdk_failure(self, auth):
        mock_sdk = MagicMock()
        mock_sdk.object.side_effect = RuntimeError("timeout")

        broker = LasairBrokerClient(auth=auth)
        with patch(
            "cobtools.query.query_lasair.lasair", return_value=mock_sdk
        ):
            with pytest.raises(
                BrokerQueryError, match="Failed to retrieve diaObject"
            ):
                broker.get_diaobject(42)

    def test_query_error_includes_object_id(self, auth):
        mock_sdk = MagicMock()
        mock_sdk.object.side_effect = RuntimeError("not found")

        broker = LasairBrokerClient(auth=auth)
        with patch(
            "cobtools.query.query_lasair.lasair", return_value=mock_sdk
        ):
            with pytest.raises(BrokerQueryError, match="99"):
                broker.get_diaobject(99)


# ---------------------------------------------------------------------------
# get_lightcurve
# ---------------------------------------------------------------------------

class TestGetLightcurve:
    def test_returns_light_curve(self, auth):
        mock_sdk = MagicMock()
        mock_sdk.object.return_value = _raw_api_dict()

        broker = LasairBrokerClient(auth=auth)
        with patch(
            "cobtools.query.query_lasair.lasair", return_value=mock_sdk
        ):
            result = broker.get_lightcurve(42)

        assert isinstance(result, LightCurve)


# ---------------------------------------------------------------------------
# real payload fixture tests
# ---------------------------------------------------------------------------

class TestRealLasairPayload:
    def test_from_api_data_parses_real_payload(self, real_lasair_payload):
        parsed = LasairObject.from_api_data(copy.deepcopy(real_lasair_payload))

        assert isinstance(parsed, LasairObject)
        assert str(parsed.diaObjectId) == "313963359482937364"
        assert len(parsed.diaSourcesList) > 0
        assert parsed.lasairData.nDiaSources == 296

    def test_get_diaobject_with_real_payload(self, auth, real_lasair_payload):
        mock_sdk = MagicMock()
        mock_sdk.object.return_value = copy.deepcopy(real_lasair_payload)

        broker = LasairBrokerClient(auth=auth)
        with patch(
            "cobtools.query.query_lasair.lasair", return_value=mock_sdk
        ):
            result = broker.get_diaobject(313963359482937364)

        assert isinstance(result, LasairObject)
        assert len(result.diaSourcesList) > 0

    def test_get_lightcurve_with_real_payload(self, auth, real_lasair_payload):
        mock_sdk = MagicMock()
        mock_sdk.object.return_value = copy.deepcopy(real_lasair_payload)

        broker = LasairBrokerClient(auth=auth)
        with patch(
            "cobtools.query.query_lasair.lasair", return_value=mock_sdk
        ):
            lc = broker.get_lightcurve(313963359482937364)

        assert isinstance(lc, LightCurve)
        assert len(lc.time_axis) > 0
        assert len(lc.time_axis) == len(lc.flux) == len(lc.flux_err)

    def test_passes_diaobject_kwargs(self, auth):
        mock_sdk = MagicMock()
        mock_sdk.object.return_value = _raw_api_dict()

        broker = LasairBrokerClient(auth=auth)
        with patch(
            "cobtools.query.query_lasair.lasair", return_value=mock_sdk
        ):
            broker.get_lightcurve(42, diaobject_kwargs={"lite": True})

        mock_sdk.object.assert_called_once_with(42, lite=True)

    def test_defaults_to_empty_kwargs(self, auth):
        """Calling without optional kwargs should not raise."""
        mock_sdk = MagicMock()
        mock_sdk.object.return_value = _raw_api_dict()

        broker = LasairBrokerClient(auth=auth)
        with patch(
            "cobtools.query.query_lasair.lasair", return_value=mock_sdk
        ):
            result = broker.get_lightcurve(42)

        assert isinstance(result, LightCurve)
