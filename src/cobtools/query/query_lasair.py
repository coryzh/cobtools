from cobtools.data_models.lsst_lasair import LasairObject
from cobtools.data_models.light_curve import LightCurve
from lasair import lasair_client as lasair
from cobtools.query.base import (
    BrokerCapabilities,
    BrokerClient,
    BrokerAuthError,
    BrokerQueryError
)


class LasairBrokerClient(BrokerClient[LasairObject]):
    DEFAULT_ENDPOINT = "https://api.lasair.lsst.ac.uk/api"

    capabilities = BrokerCapabilities(
        object_lookup=True,
        lightcurve_retrieval=True,
        image_retrieval=True
    )

    def _build_client(self):
        if not self.auth.token:
            raise BrokerAuthError(
                "Lasair API token is required for authentication."
            )

        try:
            return lasair(
                token=self.auth.token, endpoint=self.DEFAULT_ENDPOINT
            )
        except Exception as e:
            raise BrokerAuthError(
                f"Failed to authenticate with Lasair API: {e}"
            ) from e

    def get_diaobject(self, diaobject_id: int, **kwargs) -> LasairObject:
        try:
            raw_data = self.client.object(diaobject_id, **kwargs)
        except Exception as e:
            raise BrokerQueryError(
                f"Failed to retrieve diaObject with ID {diaobject_id}: {e}"
            ) from e

        return LasairObject.from_api_data(raw_data)

    def get_lightcurve(
            self, diaobject_id: int, diaobject_kwargs=None,
            lightcurve_kwargs=None
    ) -> LightCurve:
        diaobject_kwargs = diaobject_kwargs or {}
        lightcurve_kwargs = lightcurve_kwargs or {}

        lasair_object = self.get_diaobject(diaobject_id, **diaobject_kwargs)
        return lasair_object.get_lightcurve(**lightcurve_kwargs)
