"""
Data models defined for the Lasair data objects. For more information, see the
Lasair documentation [1]_.

Classes
-------
LasairData
    A data class representing a data object from the Lasair database, which
    includes metadata provided by Lasair.

LasairObject
    A data class representing a single object from the Lasair database. This
    class is a wrapper that combines the LSST diaObject and Lasair-derived
    metadata.

Reference
---------
.. [1] Lasair documentation: https://lasair-lsst.readthedocs.io/en/main/
"""

from dataclasses import dataclass, asdict, field
from cobtools.data_models.light_curve import LightCurve
from cobtools.data_models.lsst import DiaObject, DiaSource, DiaForcedSource
from typing import List, Optional
import pandas as pd


@dataclass
class LasairData:
    nDiaSources: Optional[int] = field(default=None)
    firstDiaSourceMjdTai: Optional[float] = field(default=None)
    lastDiaSourceMjdTai: Optional[float] = field(default=None)
    glat: Optional[float] = field(default=None)
    ebv: Optional[float] = field(default=None)
    rasex: Optional[float] = field(default=None)
    decsex: Optional[float] = field(default=None)
    ec_lon: Optional[float] = field(default=None)
    ec_lat: Optional[float] = field(default=None)
    g_lon: Optional[float] = field(default=None)
    g_lat: Optional[float] = field(default=None)
    now_mjd: Optional[float] = field(default=None)
    mjdmin_ago: Optional[float] = field(default=None)
    mjdmax_ago: Optional[float] = field(default=None)
    discMjd: Optional[float] = field(default=None)
    discUtc: Optional[str] = field(default=None)
    discMag: Optional[float] = field(default=None)
    discFilter: Optional[str] = field(default=None)
    latestMjd: Optional[float] = field(default=None)
    latestUtc: Optional[str] = field(default=None)
    latestMag: Optional[float] = field(default=None)
    latestFilter: Optional[str] = field(default=None)
    peakMjd: Optional[float] = field(default=None)
    peakUtc: Optional[str] = field(default=None)
    peakMag: Optional[float] = field(default=None)
    peakFilter: Optional[str] = field(default=None)
    sherlock: Optional[dict] = field(default=None)
    TNS: Optional[dict] = field(default=None)
    annotations: Optional[List[dict]] = field(default=None)
    imageUrls: Optional[List[dict]] = field(default=None)


@dataclass(frozen=True)
class LasairObject:
    diaObjectId: int
    lasairData: LasairData
    diaObject: DiaObject
    diaSourcesList: List[DiaSource]
    diaForcedSourcesList: List[DiaForcedSource]

    def info(self) -> str:
        return (
            f"diaObjectId: {self.diaObjectId}\n"
            f"ra, dec: {self.diaObject.ra}, {self.diaObject.decl}\n"
            f"glat, glon: {self.lasairData.glat}, {self.lasairData.g_lon}\n"
            f"Discovery: {self.diaObject.firstDiaSourceMjdTai}\n"
            f"Latest: {self.diaObject.lastDiaSourceMjdTai}\n"
            f"nDiaSources: {self.lasairData.nDiaSources}\n"
            "Type: "
            f"{self.lasairData.sherlock.get('classification', 'Unknown')}"
        )

    def __str__(self) -> str:
        return self.info()

    @classmethod
    def from_api_data(cls, data: dict) -> "LasairObject":
        """
        Create a LasairObject instance from a nested dictionary
        retrieved from the Lasair API.
        """
        # Convert the nested dictionary for diaObject into a DiaObject instance
        if 'diaObject' in data and isinstance(data['diaObject'], dict):
            data['diaObject'] = DiaObject(**data['diaObject'])

        if 'lasairData' in data and isinstance(data['lasairData'], dict):
            data['lasairData'] = LasairData(**data['lasairData'])

        if 'diaSourcesList' in data and isinstance(
            data['diaSourcesList'], list
        ):
            data['diaSourcesList'] = [
                DiaSource(**source) for source in data['diaSourcesList']
            ]

        if 'diaForcedSourcesList' in data and isinstance(
            data['diaForcedSourcesList'], list
        ):
            data['diaForcedSourcesList'] = [
                DiaForcedSource(**source)
                for source in data['diaForcedSourcesList']
            ]

        return cls(**data)

    def get_lightcurve_df(
            self,
            option: Optional[str] = "diaSources",
            band: Optional[str] = "all"
    ) -> pd.DataFrame:
        if option == "diaSources":
            if len(self.diaSourcesList) == 0:
                raise ValueError("No diaSources available for this object.")
            df = pd.DataFrame(
                asdict(source) for source in self.diaSourcesList
            )
        elif option == "diaForcedSources":
            if len(self.diaForcedSourcesList) == 0:
                raise ValueError(
                    "No diaForcedSources available for this object."
                )
            df = pd.DataFrame(
                asdict(source) for source in self.diaForcedSourcesList
            )
        else:
            raise ValueError(
                "Invalid option. Choose 'diaSources' or 'diaForcedSources'."
            )

        if band not in ["all", "u", "g", "r", "i", "z", "y"]:
            raise ValueError(
                "Invalid band. Choose 'all', 'u', 'g', 'r', 'i', 'z', or 'y'."
            )
        if band == "all":
            return df

        else:
            df = df.query(f"band == '{band}'")
            df = df.drop(columns=["band"])

            return df.reset_index(drop=True)

    def get_lightcurve(self, **kwargs) -> LightCurve:
        df = self.get_lightcurve_df(**kwargs)

        return LightCurve(
            time_axis=df["midpointMjdTai"].to_numpy(),
            flux=df["psfFlux"].to_numpy(),
            flux_err=df["psfFluxErr"].to_numpy()
        )
