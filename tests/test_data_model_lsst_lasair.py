from cobtools.data_models.lsst_lasair import LasairData


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
