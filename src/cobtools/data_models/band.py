from dataclasses import dataclass
from importlib import resources
import json


def _load_band_data() -> dict:
    band_data_path = (
        resources.files("cobtools") / "data" / "band_info.json"
    )

    if not band_data_path.is_file():
        raise FileNotFoundError(
            f"Band data file not found at {band_data_path}"
        )

    with open(band_data_path, "r") as f:
        band_data = json.load(f)

    return band_data["bands"]


BAND_DATA = _load_band_data()


@dataclass(frozen=True)
class Band:
    name: str

    def __post_init__(self):
        if self.name not in BAND_DATA:
            raise ValueError(
                f"Band '{self.name}' is not defined in band data."
            )

    @property
    def zp_flam(self) -> float:
        """Return the zero-point flux for this band in erg/s/cm^2/AA."""
        return BAND_DATA[self.name]["zp_flam"]

    @property
    def zp_mag(self) -> float:
        """Return the zero-point magnitude for this band."""
        return BAND_DATA[self.name]["zp_mag"]

    @property
    def w_eff(self) -> float:
        """Return the effective wavelength for this band in Angstroms."""
        return BAND_DATA[self.name]["w_eff"]

    @property
    def system(self) -> str:
        """Return the photometric system for this band."""
        return BAND_DATA[self.name]["system"]

    def __repr__(self):
        return (
            f"Band(name='{self.name}', zp_flam={self.zp_flam}, "
            f"zp_mag={self.zp_mag}, w_eff={self.w_eff}, "
            f"system='{self.system}')"
        )
