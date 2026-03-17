import matplotlib.pyplot as plt
import json
from importlib import resources
from functools import lru_cache


@lru_cache(maxsize=1)
def _load_background_image():
    _background_image = plt.imread(
        resources.files("cobtools") / "data" / "gaia_cmd_background.png"
    )
    return _background_image


def _load_background_metadata():
    with open(
        resources.files("cobtools")
        / "data"
        / "gaia_cmd_background_metadata.json"
    ) as f:
        return json.load(f)


class GaiaCMDAxis(plt.Axes):
    """
    A matplotlib.pyplot.Axes object that displays a Gaia CMD background.
    Inherits from matplotlib.pyplot.Axes.


    Example
    -------
    import matplotlib.pyplot as plt
    from gaia_cmd_plotter import GaiaCMDAxis

    # This will create a Gaia CMD plot with a red point at (0.5, -4.0)
    fig = plt.figure()
    ax = GaiaCMDAxis(fig)
    ax.plot(0.5, -4.0, "ro")
    plt.show()
    """

    def __init__(self, fig, rect=None, **kwargs):
        """
        Constructor for GaiaCMDAxis.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
        rect : list, optional
        kwargs : dict, optional
        """
        metadata = _load_background_metadata()
        self.__left = metadata["left"]
        self.__right = metadata["right"]
        self.__bottom = metadata["bottom"]
        self.__top = metadata["top"]
        self.__extent = (self.__left, self.__right, self.__bottom, self.__top)
        self.__aspect_ratio = abs(
            (self.__right - self.__left) / (self.__top - self.__bottom)
        )

        # Set default rect
        if rect is None:
            rect = [0.125, 0.110, 0.775, 0.770]

        # Set matplotlib style
        plt.style.use(
            resources.files("cobtools") / "data" / "gaia_cmd.mplstyle"
        )

        # Call the parent class constructor
        super().__init__(fig, rect, **kwargs)

        # Set background image
        background_image = _load_background_image()
        self.imshow(
            background_image, extent=self.__extent,
            aspect=self.__aspect_ratio
        )

        # Set axis labels
        self.set_xlabel(r"$\mathrm{G_{BP} - G_{RP}}$")
        self.set_ylabel(r"$\mathrm{M_G}$")

        fig.add_axes(self)
