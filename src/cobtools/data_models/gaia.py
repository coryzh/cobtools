"""
Data model for the Gaia archive.

This module provides data classes for representing and validating Gaia-specific
identifiers and related data.

Classes
-------
SourceID
    A data class representing a Gaia source ID.
"""

from dataclasses import dataclass
from typing import Union


_VALID_DATA_RELEASES = {"dr1", "dr2", "edr3", "dr3", "dr4", "dr5"}


@dataclass(frozen=True)
class SourceID:
    """
    Data class representing a Gaia ``source_id``.

    Parameters
    ----------
    source_id : Union[int, str]
        The Gaia ``source_id`` provided to the constructor. It may be given as
        an integer or as a string representing an integer; it will be
        normalized to an integer during initialization.

    data_release : str, optional
        The data release to which the ``source_id`` belongs. Defaults to "dr3".

    Attributes
    ----------
    source_id : int
        The normalized Gaia ``source_id`` stored on the instance as an integer.

    data_release : str
        The validated data release associated with the ``source_id``.


    Raises
    ------
    ValueError
        If ``source_id`` is a float or if it cannot be converted to an integer.

    ValueError
        If ``data_release`` is not one of the valid options ("dr1", "dr2",
        "edr3", "dr3", "dr4", "dr5").
    """

    source_id: Union[int, str]
    data_release: str = "dr3"

    def __post_init__(self) -> None:
        # Ensure the input is not a float
        if isinstance(self.source_id, float):
            raise ValueError("source_id must not be a float")

        # Convert to integer if it's a string
        try:
            object.__setattr__(self, "source_id", int(self.source_id))
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"source_id must be an integer or a string representing an "
                f"integer: {e}"
            ) from e

        if self.data_release not in _VALID_DATA_RELEASES:
            raise ValueError(
                f"data_release must be one of {_VALID_DATA_RELEASES}: "
                f"{self.data_release}"
            )

    @property
    def designation(self) -> str:
        """
        The Gaia source designation string, which is derived from the
        ``source_id`` and ``data_release``.

        Returns
        -------
        str
            The Gaia source designation string.
        """
        return f"Gaia {self.data_release.upper()} {self.source_id}"
