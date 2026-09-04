from contextlib import nullcontext
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import click
from click.testing import CliRunner

from cobtools.cli.astrometry.vpec_from_source_id import (
    _get_astrometry_from_source_id,
    calc_vpec,
    display_results,
)

ASTROMETRY = {
    "source_id": 123,
    "ra": 140.6, "dec": -63.3,
    "parallax": 0.5, "parallax_error": 0.1,
    "pmra": -3.16, "pmra_error": 0.03,
    "pmdec": 4.25, "pmdec_error": 0.03,
}


def _patch_console():
    """Avoid rich's live status output cluttering captured test output."""
    mock_console_cls = MagicMock()
    mock_console_cls.return_value.status.return_value = nullcontext()
    return patch(
        "cobtools.cli.astrometry.vpec_from_source_id.Console",
        mock_console_cls,
    )


def test_display_results_formats_output(capsys):
    results = np.tile(np.array([1.0, 2.0, 3.0]), (5, 1))

    display_results(results, conf=0.5, n_samples=3)

    out = capsys.readouterr().out
    assert "dist:     2.00 +0.50/-0.50 kpc" in out
    assert "vpec:     2.00 +0.50/-0.50 km/s" in out
    assert "Number of samples: 3" in out


def test_get_astrometry_from_source_id_raises_when_no_results():
    mock_query = MagicMock()
    mock_query.return_value.query_result.return_value = None
    mock_query_module = MagicMock(SingleSourceUsefulInfoQuery=mock_query)

    with patch.dict(
        "sys.modules", {"cobtools.query.query_gaia": mock_query_module}
    ):
        with pytest.raises(click.ClickException, match="No results found"):
            _get_astrometry_from_source_id(123, dr="dr3")


def test_get_astrometry_from_source_id_raises_on_query_error():
    mock_query = MagicMock()
    mock_query.return_value.query_result.side_effect = RuntimeError("boom")
    mock_query_module = MagicMock(SingleSourceUsefulInfoQuery=mock_query)

    with patch.dict(
        "sys.modules", {"cobtools.query.query_gaia": mock_query_module}
    ):
        with pytest.raises(click.ClickException, match="Error querying"):
            _get_astrometry_from_source_id(123, dr="dr3")


def test_get_astrometry_from_source_id_returns_expected_dict():
    row = {col: value for col, value in ASTROMETRY.items()}
    mock_result = MagicMock()
    mock_result.__len__.return_value = 1
    mock_result.__getitem__.return_value = row

    mock_query = MagicMock()
    mock_query.return_value.query_result.return_value = mock_result
    mock_query_module = MagicMock(SingleSourceUsefulInfoQuery=mock_query)

    with patch.dict(
        "sys.modules", {"cobtools.query.query_gaia": mock_query_module}
    ):
        result = _get_astrometry_from_source_id(123, dr="dr3")

    assert result == row
    mock_query.assert_called_once_with(source_id=123, data_release="dr3")


def test_cli_rejects_invalid_dist_source():
    result = CliRunner().invoke(
        calc_vpec,
        [
            "--source_id", "123", "--rv", "10", "--rv_error", "1",
            "--dist_source", "unknown",
        ],
    )

    assert result.exit_code == 2
    assert "Invalid value for '--dist_source'" in result.output


def test_cli_gaia_distance_source_uses_dist_method(capsys):
    dummy_dist = np.array([1.0, 2.0, 3.0])
    dummy_vpec = np.tile(np.array([1.0, 2.0, 3.0]), (4, 1))

    with (
        _patch_console(),
        patch(
            "cobtools.cli.astrometry.vpec_from_source_id"
            "._get_astrometry_from_source_id",
            return_value=ASTROMETRY,
        ),
        patch(
            "cobtools.cli.astrometry.vpec_from_source_id"
            "._get_distance_samples",
            return_value=dummy_dist,
        ) as mock_get_dist,
        patch(
            "cobtools.astrometry.kinematics.peculiar_velocity",
            return_value=dummy_vpec,
        ) as mock_vpec,
    ):
        result = CliRunner().invoke(
            calc_vpec,
            [
                "--source_id", "123", "--rv", "10", "--rv_error", "1",
                "--dist_source", "gaia", "--dist_method", "inv",
                "--conf", "0.5", "--seed", "1",
            ],
        )

    assert result.exit_code == 0, result.output
    mock_get_dist.assert_called_once_with(
        ASTROMETRY["parallax"], ASTROMETRY["parallax_error"], method="inv"
    )
    mock_vpec.assert_called_once()
    assert "dist:" in result.output
    assert "vpec:" in result.output


def test_cli_gaia_distance_source_prompts_for_method_when_omitted():
    dummy_dist = np.array([1.0, 2.0, 3.0])
    dummy_vpec = np.tile(np.array([1.0, 2.0, 3.0]), (4, 1))

    with (
        _patch_console(),
        patch(
            "cobtools.cli.astrometry.vpec_from_source_id"
            "._get_astrometry_from_source_id",
            return_value=ASTROMETRY,
        ),
        patch(
            "cobtools.cli.astrometry.vpec_from_source_id"
            "._get_distance_samples",
            return_value=dummy_dist,
        ) as mock_get_dist,
        patch(
            "cobtools.astrometry.kinematics.peculiar_velocity",
            return_value=dummy_vpec,
        ),
    ):
        result = CliRunner().invoke(
            calc_vpec,
            [
                "--source_id", "123", "--dr", "dr3", "--rv", "10",
                "--rv_error", "1", "--dist_source", "gaia",
            ],
            input="inv\n",
        )

    assert result.exit_code == 0, result.output
    mock_get_dist.assert_called_once_with(
        ASTROMETRY["parallax"], ASTROMETRY["parallax_error"], method="inv"
    )


def test_cli_user_distance_source_skips_dist_method(capsys):
    # user-input distance path draws 10000 samples internally
    dummy_vpec = np.tile(np.ones(10000), (4, 1))

    with (
        _patch_console(),
        patch(
            "cobtools.cli.astrometry.vpec_from_source_id"
            "._get_astrometry_from_source_id",
            return_value=ASTROMETRY,
        ),
        patch(
            "cobtools.cli.astrometry.vpec_from_source_id"
            "._get_distance_samples",
        ) as mock_get_dist,
        patch(
            "cobtools.astrometry.kinematics.peculiar_velocity",
            return_value=dummy_vpec,
        ),
    ):
        result = CliRunner().invoke(
            calc_vpec,
            [
                "--source_id", "123", "--rv", "10", "--rv_error", "1",
                "--dist_source", "user", "--dist", "5.0",
                "--dist_error", "0.5", "--conf", "0.5", "--seed", "1",
            ],
        )

    assert result.exit_code == 0, result.output
    mock_get_dist.assert_not_called()
    assert "dist:" in result.output
