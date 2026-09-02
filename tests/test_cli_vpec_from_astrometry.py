from unittest.mock import patch

import numpy as np
from click.testing import CliRunner

from cobtools.cli.astrometry.vpec_from_astrometry import (
    calc_vpec,
    display_results,
)


def test_display_results_formats_components_and_sample_count(capsys):
    results = np.array(
        [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0],
            [10.0, 20.0, 30.0],
        ]
    )

    display_results(results, conf=0.5, n_samples=3)

    assert capsys.readouterr().out == (
        "   U:     2.00 +0.50/-0.50 km/s  [1.50, 2.50] km/s (50% CI)\n"
        "   V:     5.00 +0.50/-0.50 km/s  [4.50, 5.50] km/s (50% CI)\n"
        "   W:     8.00 +0.50/-0.50 km/s  [7.50, 8.50] km/s (50% CI)\n"
        "vpec:    20.00 +5.00/-5.00 km/s  [15.00, 25.00] km/s (50% CI)\n"
        "Number of samples: 3\n"
    )


def test_cli_forwards_seeded_monte_carlo_samples():
    expected_rng = np.random.RandomState(7)
    expected_samples = [
        expected_rng.normal(value, error, 4)
        for value, error in ((1.0, 0.1), (2.0, 0.2), (3.0, 0.3), (4.0, 0.4))
    ]
    mock_results = np.zeros((4, 4))

    with (
        patch(
            "cobtools.cli.astrometry.vpec_from_astrometry.peculiar_velocity",
            return_value=mock_results,
        ) as mock_peculiar_velocity,
        patch(
            "cobtools.cli.astrometry.vpec_from_astrometry.display_results"
        ) as mock_display_results,
    ):
        result = CliRunner().invoke(
            calc_vpec,
            [
                "--ra",
                "10",
                "--dec",
                "20",
                "--pmra",
                "1",
                "--pmra_error",
                "0.1",
                "--pmdec",
                "2",
                "--pmdec_error",
                "0.2",
                "--dist",
                "3",
                "--dist_error",
                "0.3",
                "--rv",
                "4",
                "--rv_error",
                "0.4",
                "--conf",
                "0.5",
                "--n_samples",
                "4",
                "--seed",
                "7",
            ],
        )

    assert result.exit_code == 0
    mock_peculiar_velocity.assert_called_once()
    call_kwargs = mock_peculiar_velocity.call_args.kwargs
    assert call_kwargs["ra"] == 10
    assert call_kwargs["dec"] == 20
    np.testing.assert_allclose(call_kwargs["pmra_cosdec"], expected_samples[0])
    np.testing.assert_allclose(call_kwargs["pmdec"], expected_samples[1])
    np.testing.assert_allclose(call_kwargs["dist"], expected_samples[2])
    np.testing.assert_allclose(call_kwargs["rv"], expected_samples[3])
    mock_display_results.assert_called_once_with(mock_results, 0.5, 4)


def test_cli_rejects_invalid_option_values():
    invalid_options = (
        ("--ra", "361"),
        ("--dec", "-91"),
        ("--pmra_error", "0"),
        ("--dist", "0"),
        ("--rv", "300001"),
        ("--conf", "1"),
        ("--n_samples", "0"),
    )

    base_args = [
        "--ra",
        "10",
        "--dec",
        "20",
        "--pmra",
        "1",
        "--pmra_error",
        "0.1",
        "--pmdec",
        "2",
        "--pmdec_error",
        "0.2",
        "--dist",
        "3",
        "--dist_error",
        "0.3",
        "--rv",
        "4",
        "--rv_error",
        "0.4",
    ]

    for option, value in invalid_options:
        result = CliRunner().invoke(calc_vpec, base_args + [option, value])

        assert result.exit_code == 2
        assert "Invalid value for" in result.output
