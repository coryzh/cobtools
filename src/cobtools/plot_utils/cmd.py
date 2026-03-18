"""
cmd.py
======

This module provides tools for creating Color-Magnitude Diagrams (CMDs)
using matplotlib. It includes a customised matplotlib Axes class that has a
predefined background image and metadata.

Functions:
- `_load_background_image`: Load the Gaia CMD background image.
- `_load_background_metadata`: Load metadata for the Gaia CMD background.

Classes:
- `GaiaCMDAxis`: A custom matplotlib Axes for Gaia CMDs.
"""
import matplotlib.pyplot as plt
import json
import numpy as np
from importlib import resources
from functools import lru_cache
from matplotlib import style


@lru_cache(maxsize=1)
def _load_background_image() -> np.ndarray:
    """
    Load the Gaia CMD background image.

    Returns
    -------
    np.ndarray
        The background image as a numpy array.
    """
    _background_image = plt.imread(
        resources.files("cobtools") / "data" / "gaia_cmd_background.png"
    )
    return _background_image


def _load_background_metadata() -> dict:
    """
    Load the meta data used for positioning the CMD background image.

    Returns
    -------
    dict
        The background metadata as a dictionary.
    """
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
    from cobtools.plot_utils.cmd import GaiaCMDAxis

    # This will create a Gaia CMD plot with a red point at (0.5, -4.0)
    fig = plt.figure()
    ax = GaiaCMDAxis(fig)
    ax.plot(0.5, -4.0, "ro")
    plt.show()

    # To use a more publication-ready style, use the style_context method:
    with GaiaCMDAxis.style_context():
        fig = plt.figure()
        ax = GaiaCMDAxis(fig)
        ax.plot(0.5, -4.0, "ro")
        plt.show()
    """

    @staticmethod
    def style_context():
        """
        Return a matplotlib style.context configured for the Gaia CMD style.
        Usage
        -----
        with GaiaCMDAxis._style_context():
            fig = plt.figure()
            ax = GaiaCMDAxis(fig)
            ...
        """
        return style.context(
            resources.files("cobtools") / "data" / "gaia_cmd.mplstyle"
        )

    def __init__(self, fig, rect=None, **kwargs):
        """
        Constructor for GaiaCMDAxis.
        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure to which the axis will be added.
        rect : list, optional
            A list of [left, bottom, width, height] that defines the position
            of the axis in the figure. If None, a default rect of
            [0.125, 0.110, 0.775, 0.770] will be used.
        **kwargs : dict
            Additional keyword arguments to pass to the parent class
            constructor matplotlib.pyplot.Axes.__init__().
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
