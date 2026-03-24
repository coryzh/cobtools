import pytest
from cobtools.data_models.band import Band, _load_band_data


BAND_DATA = _load_band_data()


class TestBand:
    def test_band_creation(self):
        band = Band(name="gaia_g")
        assert band.name == BAND_DATA["gaia_g"]["name"]
        assert band.zp_flam == BAND_DATA["gaia_g"]["zp_flam"]
        assert band.zp_mag == BAND_DATA["gaia_g"]["zp_mag"]
        assert band.w_eff == BAND_DATA["gaia_g"]["w_eff"]
        assert band.system == BAND_DATA["gaia_g"]["system"]

    def test_invalid_band_name(self):
        invalid_band = "invalid_band"
        with pytest.raises(
            ValueError, match=f"Band '{invalid_band}'"
            " is not defined in band data."
        ):
            Band(name=invalid_band)

    def test_lsst_bands(self):
        lsst_bands = [f"lsst_{band}" for band in "ugrizy"]
        for band_name in lsst_bands:
            band = Band(name=band_name)
            assert band.name == BAND_DATA[band_name]["name"]
            assert band.zp_flam == BAND_DATA[band_name]["zp_flam"]
            assert band.zp_mag == BAND_DATA[band_name]["zp_mag"]
            assert band.w_eff == BAND_DATA[band_name]["w_eff"]
            assert band.system == BAND_DATA[band_name]["system"]
