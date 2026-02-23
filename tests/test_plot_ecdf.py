import matplotlib.pyplot as plt
import numpy as np
from cobtools.plot_utils import ecdf


def test_plot_ecdf():
    data = np.random.normal(loc=0, scale=1, size=1000)
    fig, ax = plt.subplots()
    x, y = ecdf.get_ecdf(data)
    ecdf.plot_ecdf(data, ax=ax)
    ax.set_ylim(0, 1)
    plt.show()
    plt.close(fig)


if __name__ == "__main__":
    test_plot_ecdf()
