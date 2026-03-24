"""
This module provides wrapper objects around the astroquery.gaia module to
facilitate querying the Gaia archive in different ways.

Classes
-------
SingleSourceQuery
    Abstract base class that defines the interface for querying the Gaia
    archive for a single source. Subclasses must implement the ``query_str``
    property and can utilize the ``query_result`` method to retrieve results.
SingleSourceFullGaiaQuery
    Concrete implementation of ``SingleSourceQuery`` that retrieves all
    available columns for a given source_id from the Gaia main source table.

Examples
--------
Query the Gaia DR3 archive for a specific source:

    >>> query = SingleSourceFullGaiaQuery(
    ... source_id=123456789, data_release="dr3"
    ... )
    >>> results = query.query_result()
    >>> print(results)

Notes
-----
The module requires the astroquery library to be installed and configured with
access to the Gaia archive. Queries are executed via the Gaia TAP service and
results are returned as astropy Table objects.

It also uses the functools.cached_property decorator (Python 3.8+) to cache the
Gaia job object. cobtools depends on Python 3.10+, so this is compatible.

See Also
--------
astroquery.gaia : Gaia archive query interface
astropy.table.Table : Table data structure for query results
query_gaia.py
"""

from astroquery.gaia import Gaia
from astroquery.utils.tap.model.job import Job
from abc import ABC, abstractmethod
from astropy.table import Table
from textwrap import dedent
from functools import cached_property
from cobtools.data_models.gaia import SourceID


class SingleSourceQuery(ABC):
    """
    Abstract base class for querying the Gaia archive.

    .. :noindex:

    This class provides a framework for querying the Gaia archive. Subclasses
    must implement the ``query_str`` property to define the ADQL query string.
    The ``query_result`` method is implemented in the base class and can be
    used as-is or overridden by subclasses to customize the behavior.

    Parameters
    ----------
    source_id : str | int
        The ``source_id`` to query. Must be an integer or a string containing
        only numeric characters.
    data_release : str
        The Gaia data release to use.

    Attributes
    ----------
    source_id_obj : SourceID
        A SourceID object tha encapsulates the source_id and data_release
        information.

    Properties
    ----------
    query_str : str
        The ADQL query string for the specified ``source_id``.

        :noindex:

    job : Job
        Cached property that launches the Gaia query job and returns the
        ``astroquery.utils.tap.model.job.Job`` object. Handles errors if the
        query does not complete successfully.

        :noindex:

    Methods
    -------
    query_result() -> Table
        Retrieve the query results as an ``astropy.table.Table`` object.

        :noindex:

    Raises
    ------
    ValueError
        If ``source_id`` is not an integer or a string containing only numeric
        characters. If ``data_release`` is not one of the valid options
        ("dr1", "dr2", "edr3", "dr3", "dr4", "dr5").
    RuntimeError
        If the Gaia query job does not complete successfully or if there is an
        error while fetching the query results.
    """

    def __init__(self, source_id: int | str, data_release: str = "dr3"):
        try:
            source_id_obj = SourceID(source_id, data_release)
        except ValueError as e:
            raise ValueError(f"Invalid source_id or data_release: {e}") from e

        self.source_id_obj = source_id_obj

    @property
    @abstractmethod
    def query_str(self) -> str:
        """
        The ADQL query string to retrieve data for the specified ``source_id``.

        Returns
        -------
        str
            The ADQL query string.
        """
        ...

    @cached_property
    def job(self) -> Job:
        """
        The Gaia job object that will be used to execute the query.

        Returns
        -------
        Job
            The astroquery.utils.tap.model.job.Job object representing the
            Gaia query job.
        """
        job = Gaia.launch_job(self.query_str)
        phase = job.get_phase()
        if phase != 'COMPLETED':
            raise RuntimeError(
                f"Query to the {self.source_id_obj.data_release} main table "
                f"did not complete successfully. Job status: {phase}."
            )
        return job

    def query_result(self) -> Table:
        """
        Query the Gaia archive for the specified ``source_id``.

        Returns
        -------
        Table
            The query results as an ``astropy.table.Table object``.
        """
        job = self.job  # Access the cached job property
        try:
            return job.get_results()
        except Exception as e:
            raise RuntimeError(
                f"Error occurred while fetching query results: {e}"
            ) from e


class SingleSourceFullGaiaQuery(SingleSourceQuery):
    """
    Concrete implementation of SingleSourceQuery for querying the Gaia archive.

    This class retrieves the full set of columns for a given ``source_id``
    from the main Gaia source table.

    Methods
    ----------
    query_str : str
        The ADQL query string to retrieve all columns for the specified
        ``source_id``.
    """

    @property
    def query_str(self) -> str:
        """
        The ADQL query to retrieve all columns for a given source_id
        from the Gaia archive.

        Returns
        -------
        str
            The ADQL query string.
        """
        query = dedent(
            f"""
            SELECT
                *
            FROM
                gaia{self.source_id_obj.data_release}.gaia_source
            WHERE
                source_id = {self.source_id_obj.source_id}
            """
        ).strip()

        return query
