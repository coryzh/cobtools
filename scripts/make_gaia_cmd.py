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


def change_axislimit():
    fig = plt.figure(figsize=(10, 10))
    ax = GaiaCMDAxis(fig)
    ax.plot(0.5, -4.0, "ro")

    # Change x-axis limits
    ax.set_xlim(-5, 10.0)

    # Change y-axis limits
    ax.set_ylim(25.0, -10)

    plt.show()


def test_image_anchoring():
    fig = plt.figure()
    ax = GaiaCMDAxis(fig)

    # Plot points at the corners of the extent
    ax.plot([-1.5, -1.5, 5.4, 5.4], [19.0, -5.0, -5.0, 19.0], "ro")

    # Change axis limits to test anchoring
    ax.set_xlim(-5, 10)
    ax.set_ylim(-10, 25)

    plt.show()


if __name__ == "__main__":
    test_image_anchoring()
