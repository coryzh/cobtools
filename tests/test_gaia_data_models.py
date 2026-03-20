import pytest
from cobtools.data_models.gaia import SourceID


class TestSourceID:
    def test_source_id_creation(self):
        test_id = SourceID(123456789)
        assert test_id.source_id == 123456789

    def test_source_id_equality(self):
        test_id_1 = SourceID(123)
        test_id_2 = SourceID(123)
        assert test_id_1 == test_id_2

    def test_source_id_inequality(self):
        test_id_1 = SourceID(123)
        test_id_2 = SourceID(456)
        assert test_id_1 != test_id_2

    def test_valid_string_source_id(self):
        test_id = SourceID("123456789")
        assert test_id.source_id == 123456789
        assert type(test_id.source_id) is int

    def test_invalid_string_source_id(self):
        with pytest.raises(ValueError):
            SourceID("not_a_number")

    def test_float_source_id(self):
        with pytest.raises(ValueError):
            SourceID(123.456)
