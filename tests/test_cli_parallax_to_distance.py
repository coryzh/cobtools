import numpy as np
from click.testing import CliRunner
from unittest.mock import MagicMock, patch

from cobtools.cli.astrometry.parallax_to_distance import (
    display_results,
    estimate_distance,
)


def test_display_results_reports_median_interval_and_method(capsys):
    display_results(
        np.array([1.0, 2.0, 3.0]), conf=0.5, method="xrb_exp_prior"
    )

    assert capsys.readouterr().out == (
        "Distance (median): 2.00 +0.50/-0.50 kpc\n"
        "50% equal-tailed interval: [1.50, 2.50] kpc \n"
        "Method: Bayesian (XRB exponential prior)\n"
    )


def test_cli_rejects_nonpositive_parallax_error():
    result = CliRunner().invoke(estimate_distance, ["1.0", "0"])

    assert result.exit_code == 2
    assert "0.0 is not in the range x>0." in result.output


def test_cli_rejects_invalid_confidence_level():
    result = CliRunner().invoke(
        estimate_distance, ["1.0", "0.1", "--conf", "1"]
    )

    assert result.exit_code == 2
    assert "It should be a value between 0 and 1." in result.output


def test_cli_rejects_unknown_method():
    result = CliRunner().invoke(
        estimate_distance, ["1.0", "0.1", "--method", "unknown"]
    )

    assert result.exit_code == 2
    assert "Invalid value for '--method'" in result.output


def test_cli_uses_inversion_method_and_displays_results():
    mock_inversion = MagicMock()
    mock_inversion.return_value.sample_distance.return_value = np.array(
        [1.0, 2.0, 3.0]
    )

    mock_distance_module = MagicMock(SimpleInversion=mock_inversion)
    with patch.dict(
        "sys.modules", {"cobtools.astrometry.distance": mock_distance_module}
    ):
        result = CliRunner().invoke(
            estimate_distance, ["1.0", "0.1", "--conf", "0.5"]
        )

    assert result.exit_code == 0
    mock_inversion.assert_called_once_with(1.0, 0.1)
    mock_inversion.return_value.sample_distance.assert_called_once_with(
        n_samples=10000
    )
    assert "Method: Inverted parallax" in result.output
