import numpy as np
import pytest
from cobtools.plot_utils.ecdf import get_ecdf


def test_get_ecdf_basic():
    """Test basic ECDF calculation with simple array."""
    arr = np.array([1, 2, 3, 4, 5])
    x, y = get_ecdf(arr)

    assert len(x) == len(y)
    assert x[0] == 0
    assert np.allclose(y[-1], 1.0)
    assert np.all(np.diff(x) >= 0)  # x is sorted


def test_get_ecdf_normalised():
    """Test that normalised=True produces values between 0 and 1."""
    arr = np.array([10, 20, 30, 40])
    x, y = get_ecdf(arr, normalised=True)

    assert np.all(y >= 0) and np.all(y <= 1)
    assert y[0] == 0
    assert y[-1] == 1.0


def test_get_ecdf_not_normalised():
    """Test that normalised=False produces integer counts."""
    arr = np.array([1, 2, 3])
    x, y = get_ecdf(arr, normalised=False)

    assert np.array_equal(y, np.array([0, 1, 2, 3]))


def test_get_ecdf_single_element():
    """Test ECDF with single element array."""
    arr = np.array([5.0])
    x, y = get_ecdf(arr, normalised=True)

    assert len(x) == 2
    assert len(y) == 2
    assert np.allclose(y, np.array([0.0, 1.0]))


def test_get_ecdf_duplicates():
    """Test ECDF with duplicate values."""
    arr = np.array([2, 1, 1, 2, 3])
    x, y = get_ecdf(arr, normalised=False)
    print(y)
    assert x[0] == 0
    assert y[-1] == len(arr)
    assert np.array_equal(x, np.array([0, 1, 1, 2, 2, 3]))
    assert np.array_equal(y, np.array([0, 1, 2, 3, 4, 5]))


def test_get_ecdf_negative_values():
    """Test ECDF with negative values."""
    arr = np.array([-3, -1, 0, 2, 5])
    x, y = get_ecdf(arr, normalised=True)

    assert x[0] == 0  # First x value is always 0 (inserted)
    assert x[1] == -3  # Second x value is minimum of input
    assert np.allclose(y[-1], 1.0)


def test_get_ecdf_empty_array():
    """Test ECDF with empty array."""
    arr = np.array([])
    with pytest.raises(ValueError, match="Input array must not be empty."):
        get_ecdf(arr, normalised=True)


def test_get_ecdf_list_input():
    """Test ECDF with non-array input."""
    arr = [1, 2, 3]  # This is a list, not a numpy array
    x, y = get_ecdf(arr, normalised=True)

    assert len(x) == len(y)
    assert x[0] == 0
    assert np.allclose(y[-1], 1.0)
    assert np.array_equal(x, np.array([0, 1, 2, 3]))
    assert np.array_equal(y, np.array([0.0, 1./3, 2./3, 1.0]))


def test_get_ecdf_tuple_input():
    """Test ECDF with tuple input."""
    arr = (4, 2, 1)  # This is a tuple, not a numpy array
    x, y = get_ecdf(arr, normalised=False)

    assert len(x) == len(y)
    assert x[0] == 0
    assert np.array_equal(x, np.array([0, 1, 2, 4]))
    assert np.array_equal(y, np.array([0, 1, 2, 3]))
