from pathlib import Path

from cobtools.data_models.lsst_lasair import LasairData, LasairObject
import json
import pytest


class TestLasairData:
    def test_defaults_to_none(self):
        lasair_data = LasairData()

        assert lasair_data.nDiaSources is None
        assert lasair_data.firstDiaSourceMjdTai is None
        assert lasair_data.lastDiaSourceMjdTai is None
        assert lasair_data.glat is None
        assert lasair_data.ebv is None
        assert lasair_data.rasex is None
        assert lasair_data.decsex is None
        assert lasair_data.ec_lon is None
        assert lasair_data.ec_lat is None
        assert lasair_data.g_lon is None
        assert lasair_data.g_lat is None
        assert lasair_data.now_mjd is None
        assert lasair_data.mjdmin_ago is None
        assert lasair_data.mjdmax_ago is None
        assert lasair_data.discMjd is None
        assert lasair_data.discUtc is None
        assert lasair_data.discMag is None
        assert lasair_data.discFilter is None
        assert lasair_data.latestMjd is None
        assert lasair_data.latestUtc is None
        assert lasair_data.latestMag is None
        assert lasair_data.latestFilter is None
        assert lasair_data.peakMjd is None
        assert lasair_data.peakUtc is None
        assert lasair_data.peakMag is None
        assert lasair_data.peakFilter is None
        assert lasair_data.sherlock == {}
        assert lasair_data.TNS is None
        assert lasair_data.annotations is None
        assert lasair_data.imageUrls is None

    def test_stores_provided_values(self):
        sherlock = {"classification": "SN Ia", "score": 0.99}
        tns = {"name": "SN 2026abc", "type": "SN Ia"}
        annotations = [{"topic": "quality", "value": "good"}]
        image_urls = [{"tag": "difference", "url": "https://example.com"}]

        lasair_data = LasairData(
            nDiaSources=14,
            firstDiaSourceMjdTai=60200.1,
            lastDiaSourceMjdTai=60210.4,
            glat=-23.5,
            ebv=0.04,
            rasex=150.123,
            decsex=-34.567,
            ec_lon=179.2,
            ec_lat=-2.4,
            g_lon=305.6,
            g_lat=-23.5,
            now_mjd=60211.0,
            mjdmin_ago=10.9,
            mjdmax_ago=0.6,
            discMjd=60200.1,
            discUtc="2026-03-01T02:24:00",
            discMag=20.1,
            discFilter="r",
            latestMjd=60210.4,
            latestUtc="2026-03-11T09:36:00",
            latestMag=19.2,
            latestFilter="i",
            peakMjd=60205.5,
            peakUtc="2026-03-06T12:00:00",
            peakMag=18.7,
            peakFilter="r",
            sherlock=sherlock,
            TNS=tns,
            annotations=annotations,
            imageUrls=image_urls,
        )

        assert lasair_data.nDiaSources == 14
        assert lasair_data.firstDiaSourceMjdTai == 60200.1
        assert lasair_data.lastDiaSourceMjdTai == 60210.4
        assert lasair_data.glat == -23.5
        assert lasair_data.ebv == 0.04
        assert lasair_data.rasex == 150.123
        assert lasair_data.decsex == -34.567
        assert lasair_data.ec_lon == 179.2
        assert lasair_data.ec_lat == -2.4
        assert lasair_data.g_lon == 305.6
        assert lasair_data.g_lat == -23.5
        assert lasair_data.now_mjd == 60211.0
        assert lasair_data.mjdmin_ago == 10.9
        assert lasair_data.mjdmax_ago == 0.6
        assert lasair_data.discMjd == 60200.1
        assert lasair_data.discUtc == "2026-03-01T02:24:00"
        assert lasair_data.discMag == 20.1
        assert lasair_data.discFilter == "r"
        assert lasair_data.latestMjd == 60210.4
        assert lasair_data.latestUtc == "2026-03-11T09:36:00"
        assert lasair_data.latestMag == 19.2
        assert lasair_data.latestFilter == "i"
        assert lasair_data.peakMjd == 60205.5
        assert lasair_data.peakUtc == "2026-03-06T12:00:00"
        assert lasair_data.peakMag == 18.7
        assert lasair_data.peakFilter == "r"
        assert lasair_data.sherlock == sherlock
        assert lasair_data.TNS == tns
        assert lasair_data.annotations == annotations
        assert lasair_data.imageUrls == image_urls

    def test_equal_instances_compare_equal(self):
        lasair_data_1 = LasairData(nDiaSources=3, latestFilter="g")
        lasair_data_2 = LasairData(nDiaSources=3, latestFilter="g")

        assert lasair_data_1 == lasair_data_2


class TestLasairObjectToJson:
    @pytest.fixture(scope="class")
    def lasair_object(self):
        with open("tests/dia_source_data.json", "r") as f:
            dia_sources_data = json.load(f)
        return LasairObject.from_api_data(dia_sources_data)

    def test_to_json_creates_file(self, lasair_object, tmp_path):
        output_file = tmp_path / "output.json"
        lasair_object.to_json(output_file)

        assert output_file.exists()

    def test_to_json_valid_json_content(self, lasair_object, tmp_path):
        output_file = tmp_path / "output.json"
        lasair_object.to_json(output_file)

        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert data["diaObjectId"] == lasair_object.diaObjectId

    def test_to_json_accepts_str_path(self, lasair_object, tmp_path):
        output_file = str(tmp_path / "output_str.json")
        lasair_object.to_json(output_file)

        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert data["diaObjectId"] == lasair_object.diaObjectId

    def test_to_json_accepts_path_object(self, lasair_object, tmp_path):
        output_file = Path(tmp_path) / "output_path.json"
        lasair_object.to_json(output_file)

        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert data["diaObjectId"] == lasair_object.diaObjectId


class TestLasairImageURLs:
    @pytest.fixture(scope="class")
    def lasair_data(self):
        with open("tests/dia_source_data.json", "r") as f:
            dia_sources_data = json.load(f)
        return LasairObject.from_api_data(dia_sources_data)

    def test_get_image_urls_valid_input(self, lasair_data):
        img_urls = lasair_data.image_urls(band="r", img_type="science")

        assert isinstance(img_urls, list)
        assert all(isinstance(url, str) for url in img_urls)
        assert all("Science" in url for url in img_urls)

    def test_get_image_urls_invalid_img_type(self, lasair_data):
        with pytest.raises(
            ValueError, match="Invalid img_type."
        ):
            lasair_data.image_urls(band="r", img_type="invalid_type")

    def test_get_image_urls_invalid_band(self, lasair_data):
        with pytest.raises(
            ValueError, match="Invalid band."
        ):
            lasair_data.image_urls(band="invalid_band", img_type="science")
