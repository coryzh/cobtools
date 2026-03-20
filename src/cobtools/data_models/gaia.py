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


@dataclass(frozen=True)
class SourceID:
    """
    Data class representing a Gaia source ID.

    Attributes
    ----------
    source_id : Union[int, str]
        The Gaia source ID, which can be provided as an integer or a string
        representing an integer.

    Raises
    ------
    ValueError
        If ``source_id`` is a float or if it cannot be converted to an integer.
    """

    source_id: Union[int, str]

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
