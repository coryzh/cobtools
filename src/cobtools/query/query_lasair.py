"""
Wrapper client around the Lasair API, implementing the BrokerClient interface
defined in the base layer (cobtools.query.base).

Classes
-------
LasairBrokerClient
    A wrapper client for querying the Lasair API. It encapsulates
    authentication, client initialization, and provides methods for retrieving
    diaObjects and light curves from the Lasair API. Retrieved raw data is
    parsed into structured data models defined in
    `cobtools.data_models.lsst_lasair`.
"""

from cobtools.data_models.lsst_lasair import LasairObject
from cobtools.data_models.light_curve import LightCurve
from lasair import lasair_client as lasair
from cobtools.query.base import (
    BrokerCapabilities,
    BrokerClient,
    BrokerAuthError,
    BrokerQueryError,
)


class LasairBrokerClient(BrokerClient[LasairObject]):
    """
    A wrapper client for querying the Lasair API, implementing the BrokerClient
    interface.

    Parameters
    ----------
    BrokerClient : BrokerClient
        The base class providing the interface and common structures for broker

    Methods
    -------
    get_diaobject(diaobject_id: int, **kwargs) -> LasairObject
        Retrieve a diaObject from the Lasair API by its ID, returning a
        LasairObject instance.

    get_lightcurve(
        diaobject_id: int, diaobject_kwargs=None, lightcurve_kwargs=None
    ) -> LightCurve
        Retrieve the light curve for a given diaObject ID, with optional
        parameters for both the diaObject retrieval and light curve retrieval.
        Returns a LightCurve instance.
    """

    DEFAULT_ENDPOINT = "https://api.lasair.lsst.ac.uk/api"

    capabilities = BrokerCapabilities(
        object_lookup=True,
        lightcurve_retrieval=True,
        image_retrieval=True
    )

    def _build_client(self):
        """
        Build and return the Lasair API client using the provided
        authentication.

        Raises
        ------
        BrokerAuthError
            If authentication fails due to missing token or SDK errors.

        BrokerAuthError
            If the Lasair API token is missing or invalid.
        """

        if not self.auth.token:
            raise BrokerAuthError(
                "Lasair API token is required for authentication."
            )

        try:
            endpoint = getattr(self, "endpoint", None) or self.DEFAULT_ENDPOINT
            return lasair(
                token=self.auth.token, endpoint=endpoint
            )
        except Exception as e:
            raise BrokerAuthError(
                f"Failed to authenticate with Lasair API: {e}"
            ) from e

    def get_diaobject(self, diaobject_id: int, **kwargs) -> LasairObject:
        """
        Retrieve a diaObject from the Lasair API by its ID.

        Parameters
        ----------
        diaobject_id : int
            The ID of the diaObject to retrieve.

        kwargs : dict
            Additional keyword arguments passed to the official Lasair client.
            See the Lasair API documentation for supported parameters.

        Returns
        -------
        LasairObject
            A LasairObject instance representing the retrieved diaObject.

        Raises
        ------
        BrokerQueryError
            If the retrieval of the diaObject fails.

        Notes
        -----
        Lasair API documentation:
        https://lasair-lsst.readthedocs.io/en/main/core_functions/client.html
        """

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
        """
        Retrieve the light curve for a given diaObject ID.

        Parameters
        ----------
        diaobject_id : int
            The ID of the diaObject for which to retrieve the light curve.

        diaobject_kwargs : dict, optional
            Additional keyword arguments passed to the
            :meth:`LasairBrokerClient.get_diaobject` (and ultimately to the
            underlying Lasair client ``.object(...)`` call), by default None.

        lightcurve_kwargs : dict, optional
            Additional keyword arguments for the `get_lightcurve` method of the
            LasairObject class, by default None

        Returns
        -------
        LightCurve
            A LightCurve instance representing the retrieved light curve.
        """
        diaobject_kwargs = diaobject_kwargs or {}
        lightcurve_kwargs = lightcurve_kwargs or {}

        lasair_object = self.get_diaobject(diaobject_id, **diaobject_kwargs)
        return lasair_object.get_lightcurve(**lightcurve_kwargs)

    def get_image_urls(
            self, diaobject_id: int, img_type: str, band: str, **kwargs
    ) -> list[str]:
        """
        Retrieve image URLs for a given diaObject ID.

        Parameters
        ----------
        diaobject_id : int
            The ID of the diaObject for which to retrieve image URLs.

        img_type : str
            The type of images to retrieve, must be one of "science",
            "template", "difference". Case-insensitive.

        band : str
            The photometric band for which to retrieve images
            must be one of "u", "g", "r", "i", "z", "y", or "all" for all
            bands.

        kwargs : dict
            Additional keyword arguments passed to the official Lasair client
            when retrieving the diaObject.

        Returns
        -------
        list[str]
            A list of image URLs associated with the diaObject.

        Raises
        ------
        BrokerQueryError
            If the retrieval of the diaObject or its image URLs fails.
        """
        try:
            lasair_object = self.get_diaobject(diaobject_id, **kwargs)
            return lasair_object.image_urls(img_type=img_type, band=band)
        except BrokerQueryError:
            # Re-raise BrokerQueryError unchanged
            raise
        except Exception as e:
            # Wrap other exceptions in BrokerQueryError
            raise BrokerQueryError(
                "Failed to retrieve image URLs for diaObject with ID "
                f"{diaobject_id}: {e}"
            ) from e
