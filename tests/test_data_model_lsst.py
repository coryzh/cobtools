from cobtools.data_models.lsst import DiaForcedSource, DiaObject, DiaSource


class TestDiaSource:
    def test_defaults_to_none(self):
        source = DiaSource()

        assert source.diaSourceId is None
        assert source.midpointMjdTai is None
        assert source.band is None
        assert source.psfFlux is None
        assert source.psfFluxErr is None
        assert source.reliability is None

    def test_stores_provided_values(self):
        source = DiaSource(
            diaSourceId=12345,
            midpointMjdTai=60234.5,
            band="r",
            psfFlux=125.4,
            psfFluxErr=2.1,
            reliability=0.98,
        )

        assert source.diaSourceId == 12345
        assert source.midpointMjdTai == 60234.5
        assert source.band == "r"
        assert source.psfFlux == 125.4
        assert source.psfFluxErr == 2.1
        assert source.reliability == 0.98

    def test_equal_instances_compare_equal(self):
        source_1 = DiaSource(diaSourceId=12345, band="i")
        source_2 = DiaSource(diaSourceId=12345, band="i")

        assert source_1 == source_2


class TestDiaForcedSource:
    def test_defaults_to_none(self):
        forced_source = DiaForcedSource()

        assert forced_source.midpointMjdTai is None
        assert forced_source.band is None
        assert forced_source.psfFlux is None
        assert forced_source.psfFluxErr is None

    def test_stores_provided_values(self):
        forced_source = DiaForcedSource(
            midpointMjdTai=60235.25,
            band="g",
            psfFlux=80.3,
            psfFluxErr=1.7,
        )

        assert forced_source.midpointMjdTai == 60235.25
        assert forced_source.band == "g"
        assert forced_source.psfFlux == 80.3
        assert forced_source.psfFluxErr == 1.7

    def test_unequal_instances_compare_unequal(self):
        forced_source_1 = DiaForcedSource(band="g", psfFlux=80.3)
        forced_source_2 = DiaForcedSource(band="r", psfFlux=80.3)

        assert forced_source_1 != forced_source_2


class TestDiaObject:
    def test_defaults_to_none(self):
        obj = DiaObject()

        assert obj.diaObjectId is None
        assert obj.ra is None
        assert obj.decl is None
        assert obj.firstDiaSourceMjdTai is None
        assert obj.lastDiaSourceMjdTai is None

    def test_stores_provided_values(self):
        obj = DiaObject(
            diaObjectId=54321,
            ra=150.123,
            decl=-34.567,
            firstDiaSourceMjdTai=60230.1,
            lastDiaSourceMjdTai=60240.9,
        )

        assert obj.diaObjectId == 54321
        assert obj.ra == 150.123
        assert obj.decl == -34.567
        assert obj.firstDiaSourceMjdTai == 60230.1
        assert obj.lastDiaSourceMjdTai == 60240.9

    def test_equal_instances_compare_equal(self):
        object_1 = DiaObject(diaObjectId=54321, ra=150.123, decl=-34.567)
        object_2 = DiaObject(diaObjectId=54321, ra=150.123, decl=-34.567)

        assert object_1 == object_2
