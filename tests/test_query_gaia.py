import pytest
from unittest.mock import patch, MagicMock
from astropy.table import Table
from cobtools.query.query_gaia import (
    SingleSourceQuery, SingleSourceFullGaiaQuery
)
from textwrap import dedent
import numpy as np


class TestSingleSourceQuery:
    """Tests for SingleSourceQuery abstract base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that SingleSourceQuery cannot be instantiated directly."""
        with pytest.raises(TypeError):
            SingleSourceQuery(source_id=123)

    def test_init_valid_int_source_id(self):
        """Test initialization with integer source_id."""
        query = SingleSourceFullGaiaQuery(source_id=123456)
        assert query.source_id_obj.source_id == 123456

    def test_init_valid_str_source_id(self):
        """Test initialization with string source_id."""
        query = SingleSourceFullGaiaQuery(source_id="123456")
        # Should be converted to int
        assert query.source_id_obj.source_id == 123456

    def test_init_invalid_source_id_type(self):
        """Test that invalid source_id type raises TypeError."""
        with pytest.raises(
            ValueError, match="source_id must not be a float"
        ):
            SingleSourceFullGaiaQuery(source_id=12.34)

        with pytest.raises(
            ValueError, match="source_id must be an integer or a string"
        ):
            SingleSourceFullGaiaQuery(source_id="wrong_source_id")

    def test_init_default_data_release(self):
        """Test that default data_release is 'dr3'."""
        query = SingleSourceFullGaiaQuery(source_id=123456)
        assert query.source_id_obj.data_release == "dr3"

    def test_init_custom_data_release(self):
        """Test initialization with custom data_release."""
        for release in ["dr1", "dr2", "edr3", "dr3", "dr4", "dr5"]:
            query = SingleSourceFullGaiaQuery(
                source_id=123456, data_release=release
            )
            assert query.source_id_obj.data_release == release

    def test_init_invalid_data_release(self):
        """Test that invalid data_release raises ValueError."""
        with pytest.raises(
            ValueError,
            match=(
                "Invalid source_id or data_release:"
                " data_release must be one of"
            )
        ):
            SingleSourceFullGaiaQuery(source_id=123456, data_release="dr99")


class TestSingleSourceFullGaiaQuery:
    """Tests for SingleSourceFullGaiaQuery implementation."""
    def test_query_str_format(self):
        """Test that query_str generates correct ADQL query."""
        query = SingleSourceFullGaiaQuery(
            source_id=123456, data_release="dr3"
        )
        expected = dedent(
            f"""
            SELECT
                *
            FROM
                gaiadr3.gaia_source
            WHERE
                source_id = {query.source_id_obj.source_id}
            """
        ).strip()
        assert query.query_str == expected

    def test_query_str_with_different_release(self):
        """Test query_str with different data release."""
        query = SingleSourceFullGaiaQuery(source_id=789, data_release="dr2")
        assert "gaiadr2.gaia_source" in query.query_str
        assert (
            f"source_id = {query.source_id_obj.source_id}" in query.query_str
        )

    @patch("cobtools.query.query_gaia.Gaia.launch_job")
    def test_query_result_success(self, mock_launch_job):
        """Test query_result returns table successfully."""
        mock_job = MagicMock()
        mock_job.get_phase.return_value = 'COMPLETED'
        mock_job.get_results.return_value = Table(
            names=[
                "source_id", "ra", "dec", "parallax", "pmra", "pmdec",
                "phot_g_mean_mag"
            ],
            data=[
                [4787135780363189504], [71.75571839171829],
                [-46.59034574895981], [0.38555175893640115],
                [17.106916182108442], [17.156456857994684],
                [14.051228]
            ]
        )
        mock_launch_job.return_value = mock_job

        query = SingleSourceFullGaiaQuery(source_id=4787135780363189504)
        result = query.query_result()

        assert isinstance(result, Table)
        for col in mock_job.get_results().colnames:
            assert col in result.colnames
            assert np.allclose(result[col], mock_job.get_results()[col])
