import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from cobtools.plot_utils import nk_proxy_distributions as nk

matplotlib.use("Agg")


@pytest.fixture(autouse=True)
def close_all_figures():
    yield
    plt.close("all")


def test_two_maxwellian_pdf_shape_and_values():
    x = np.linspace(0, 1000, 500)
    y = nk.two_maxwellian(x, sigma1=50.0, sigma2=250.0, w=0.4)

    assert isinstance(y, np.ndarray)
    assert y.shape == x.shape
    assert np.all(np.isfinite(y))
    assert np.all(y >= 0)


def test_two_maxwellian_cdf_is_monotonic_and_bounded():
    x = np.linspace(0, 1000, 500)
    y = nk.two_maxwellian(
        x, sigma1=50.0, sigma2=250.0, w=0.4, cumulative=True
    )

    assert np.all(np.isfinite(y))
    assert np.all(y >= 0)
    assert np.all(y <= 1)
    assert np.all(np.diff(y) >= -1e-12)


@pytest.mark.parametrize(
    "sigma1,sigma2,w",
    [
        (0.0, 100.0, 0.5),
        (100.0, -1.0, 0.5),
        (100.0, 200.0, -0.1),
        (100.0, 200.0, 1.1),
    ],
)
def test_two_maxwellian_invalid_parameters_raise(sigma1, sigma2, w):
    x = np.linspace(0, 100, 50)
    with pytest.raises(ValueError):
        nk.two_maxwellian(x, sigma1=sigma1, sigma2=sigma2, w=w)


def test_lognormal_pdf_shape_and_values():
    x = np.linspace(0.0, 1000.0, 500)
    y = nk.lognormal(x, mu=2.0, sigma=0.6)

    assert isinstance(y, np.ndarray)
    assert y.shape == x.shape
    assert np.all(np.isfinite(y))
    assert np.all(y >= 0)


def test_lognormal_cdf_is_monotonic_and_bounded():
    x = np.linspace(0.0, 1000.0, 500)
    y = nk.lognormal(x, mu=2.0, sigma=0.6, cumulative=True)

    assert np.all(np.isfinite(y))
    assert np.all(y >= 0)
    assert np.all(y <= 1)
    assert np.all(np.diff(y) >= -1e-12)


@pytest.mark.parametrize(
    "mu,sigma",
    [
        (0.0, 0.5),
        (-1.0, 0.5),
        (1.0, 0.0),
        (1.0, -0.1),
    ],
)
def test_lognormal_invalid_parameters_raise(mu, sigma):
    x = np.linspace(0, 100, 50)
    with pytest.raises(ValueError, match="mu and sigma must be positive"):
        nk.lognormal(x, mu=mu, sigma=sigma)


def test_load_data_returns_expected_structure():
    df = nk._load_data()

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    required_cols = {"type", "ref", "model", "param1", "param2"}
    assert required_cols.issubset(df.columns)


def test_make_figure_default_labels():
    fig, ax = nk.make_figure(cumulative=False)

    assert ax.get_xlabel() == "Inferred natal kick (km/s)"
    assert ax.get_ylabel() == "PDF"
    assert fig is not None
    assert ax is not None


def test_make_figure_cumulative_labels_and_ylim():
    fig, ax = nk.make_figure(cumulative=True)

    assert ax.get_xlabel() == "Inferred natal kick (km/s)"
    assert ax.get_ylabel() == "CDF"
    assert ax.get_ylim() == (0.0, 1.0)
    assert fig is not None
    assert ax is not None


def test_add_distribution_to_plot_two_maxwellian_adds_line():
    fig, ax = plt.subplots()
    x = np.linspace(0, 1000, 500)
    row = pd.Series(
        {
            "model": "two_maxwellian",
            "param1": 50.0,
            "param2": 250.0,
            "param3": 0.4,
            "type": "demo",
            "ref": "demo_ref",
        }
    )

    nk.add_distribution_to_plot(ax, x, row, cumulative=False, lw=2.0)

    assert len(ax.lines) == 1
    line = ax.lines[0]
    assert line.get_xdata().shape == x.shape
    assert line.get_ydata().shape == x.shape


def test_add_distribution_to_plot_lognormal_adds_line():
    fig, ax = plt.subplots()
    x = np.linspace(0, 1000, 500)
    row = pd.Series(
        {
            "model": "lognormal",
            "param1": 2.0,
            "param2": 0.6,
            "type": "demo",
            "ref": "demo_ref",
        }
    )

    nk.add_distribution_to_plot(ax, x, row, cumulative=True, lw=2.0)

    assert len(ax.lines) == 1


def test_add_distribution_to_plot_unknown_model_raises():
    fig, ax = plt.subplots()
    x = np.linspace(0, 100, 50)
    row = pd.Series(
        {
            "model": "not_a_model",
            "param1": 1.0,
            "param2": 1.0,
            "param3": 0.5,
            "type": "demo",
            "ref": "demo_ref",
        }
    )

    with pytest.raises(ValueError, match="Unknown model"):
        nk.add_distribution_to_plot(ax, x, row)


def test_plot_nk_distributions_with_mock_data(monkeypatch):
    mock_df = pd.DataFrame(
        [
            {
                "type": "A",
                "ref": "RefA",
                "model": "two_maxwellian",
                "param1": 50.0,
                "param2": 250.0,
                "param3": 0.5,
            },
            {
                "type": "B",
                "ref": "RefB",
                "model": "lognormal",
                "param1": 2.0,
                "param2": 0.6,
                "param3": np.nan,
            },
        ]
    )

    monkeypatch.setattr(nk, "_load_data", lambda: mock_df)

    fig, ax = nk.plot_nk_distributions(cumulative=False)

    assert fig is not None
    assert ax is not None
    assert len(ax.lines) == len(mock_df)
    assert ax.get_xlim() == (0.0, 1000.0)
    assert ax.get_legend() is not None
    assert ax.get_ylabel() == "PDF"


def test_plot_nk_distributions_cumulative_with_mock_data(monkeypatch):
    mock_df = pd.DataFrame(
        [
            {
                "type": "A",
                "ref": "RefA",
                "model": "two_maxwellian",
                "param1": 50.0,
                "param2": 250.0,
                "param3": 0.5,
            },
            {
                "type": "B",
                "ref": "RefB",
                "model": "lognormal",
                "param1": 2.0,
                "param2": 0.6,
                "param3": np.nan,
            },
        ]
    )

    monkeypatch.setattr(nk, "_load_data", lambda: mock_df)

    fig, ax = nk.plot_nk_distributions(cumulative=True)

    assert fig is not None
    assert ax is not None
    assert len(ax.lines) == len(mock_df)
    assert ax.get_ylabel() == "CDF"
    assert ax.get_ylim() == (0.0, 1.0)
