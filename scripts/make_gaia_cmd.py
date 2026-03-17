from cobtools.plot_utils.cmd import GaiaCMDAxis
import matplotlib.pyplot as plt


def make_cmd():
    fig = plt.figure()
    ax = GaiaCMDAxis(fig)
    ax.plot(0.5, -4.0, "ro")
    plt.show()


def different_rect():
    fig = plt.figure()

    # Default rect
    ax1 = GaiaCMDAxis(fig)
    ax1.plot(0.5, -4.0, "ro")

    # Custom rect (smaller axes)
    ax2 = GaiaCMDAxis(fig, rect=[0.2, 0.2, 0.6, 0.6])
    ax2.plot(1.0, -3.0, "bo")

    plt.show()


def different_figure_sizes():
    # Square figure
    fig1 = plt.figure(figsize=(8, 8))
    ax1 = GaiaCMDAxis(fig1)
    ax1.plot(0.5, -4.0, "ro")

    # Rectangular figure
    fig2 = plt.figure(figsize=(5, 12))
    ax2 = GaiaCMDAxis(fig2)
    ax2.plot(0.5, -4.0, "ro")

    plt.show()


if __name__ == "__main__":
    different_figure_sizes()
