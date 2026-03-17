import matplotlib.pyplot as plt
from unittest.mock import patch
from cobtools.plot_utils.cmd import GaiaCMDAxis


class TestGaiaCMDAxis:
    @patch("cobtools.plot_utils.cmd._load_background_metadata")
    def test_initialization(self, mock_load_metadata):
        mock_load_metadata.return_value = {
            "left": -1.0,
            "right": 1.0,
            "bottom": -5.0,
            "top": 5.0,
        }

        fig = plt.figure()
        ax = GaiaCMDAxis(fig)

        # Name mangling: _ClassName__AttributeName
        # E.g., __left in GaiaCMDAxis becomes _GaiaCMDAxis__left
        assert ax._GaiaCMDAxis__left == -1.0
        assert ax._GaiaCMDAxis__right == 1.0
        assert ax._GaiaCMDAxis__bottom == -5.0
        assert ax._GaiaCMDAxis__top == 5.0

        plt.close(fig)

    @patch("cobtools.plot_utils.cmd._load_background_metadata")
    def test_background_image_loading(self, mock_load_metadata):
        mock_load_metadata.return_value = {
            "left": -1.0,
            "right": 1.0,
            "bottom": -5.0,
            "top": 5.0,
        }

        fig = plt.figure()
        ax = GaiaCMDAxis(fig)
        # Check if the background image is loaded as an image in the axis
        assert len(ax.images) == 1

        plt.close(fig)

    def test_axis_labels(self):
        fig = plt.figure()
        ax = GaiaCMDAxis(fig)
        assert ax.get_xlabel() == r"$\mathrm{G_{BP} - G_{RP}}$"
        assert ax.get_ylabel() == r"$\mathrm{M_G}$"

        plt.close(fig)

    @patch("cobtools.plot_utils.cmd._load_background_metadata")
    def test_axis_limits(self, mock_load_metadata):
        mock_load_metadata.return_value = {
            "left": -1.0,
            "right": 1.0,
            "bottom": -5.0,
            "top": 5.0,
        }

        fig = plt.figure()
        ax = GaiaCMDAxis(fig)

        # By default, the axis limits should match extent of the background
        # image, which is specified by the loaded metadata.
        assert ax.get_xlim() == (-1.0, 1.0)
        assert ax.get_ylim() == (-5.0, 5.0)

        plt.close(fig)

    @patch("cobtools.plot_utils.cmd._load_background_metadata")
    def test_background_anchoring_with_changed_limits(
        self, mock_load_metadata
    ):
        mock_load_metadata.return_value = {
            "left": -1.0,
            "right": 1.0,
            "bottom": -5.0,
            "top": 5.0,
        }

        fig = plt.figure()
        ax = GaiaCMDAxis(fig)

        # Check the initial extent of the background image
        assert len(ax.images) == 1  # Ensure the background image is loaded
        background_image = ax.images[0]
        assert tuple(background_image.get_extent()) == (-1.0, 1.0, -5.0, 5.0)

        # Change the axis limits
        ax.set_xlim(-2.0, 2.0)
        ax.set_ylim(-6.0, 6.0)

        # The background image's extent should remain the same
        assert tuple(background_image.get_extent()) == (-1.0, 1.0, -5.0, 5.0)
        plt.close(fig)

    def test_override_axis_labels(self):
        fig = plt.figure()
        ax = GaiaCMDAxis(fig)
        ax.plot(0.5, -4.0, "ro")
        ax.set_xlabel("Custom X Label")
        ax.set_ylabel("Custom Y Label")
        assert ax.get_xlabel() == "Custom X Label"
        assert ax.get_ylabel() == "Custom Y Label"

        plt.close(fig)

    def test_override_axis_limits(self):
        fig = plt.figure()
        ax = GaiaCMDAxis(fig)
        ax.plot(0.5, -4.0, "ro")
        ax.set_xlim(-5, 10.0)
        # y-axis is inverted here on purpose to
        # test if the GaiaCMDAxis class will restore the original axis limits
        # (it shouldn't)
        ax.set_ylim(-10.0, 25.0)
        assert ax.get_xlim() == (-5, 10.0)
        assert ax.get_ylim() == (-10.0, 25.0)

        plt.close(fig)
