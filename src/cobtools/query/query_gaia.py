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


class SingleSourceQuery(ABC):
    """
    .. :noindex:

    Abstract base class for querying the Gaia archive.

    This class provides a framework for querying the Gaia archive. Subclasses
    must implement the ``query_str`` property to define the ADQL query string.
    The ``query_result`` method is implemented in the base class and can be
    used as-is or overridden by subclasses to customize the behavior.

    Attributes
    ----------
    source_id : int or str
        The ``source_id`` to query. Must be an integer or a string containing
        only numeric characters.
    data_release : str
        The Gaia data release to use. Valid options are "dr1", "dr2", "edr3",
        "dr3", "dr4", and "dr5". Defaults to "dr3".

    Properties
    ----------
    query_str : str
        .. :no-index:

        Abstract property that defines the ADQL query string for the specified
        ``source_id``. Must be implemented by subclasses.
    job : Job
        .. :no-index:

        Cached property that launches the Gaia query job and returns the
        ``astroquery.utils.tap.model.job.Job`` object. Handles errors if the
        query does not complete successfully.

    Methods
    -------
    query_result() -> Table
        .. :no-index:

        Retrieve the query results as an
        ``astropy.table.Table`` object. Must be implemented by subclasses.

    Raises
    ------
    TypeError
        If ``source_id`` is not an integer or a string containing only numeric
        characters.
    ValueError
        If ``data_release`` is not one of the valid options ("dr1", "dr2",
        "edr3", "dr3", "dr4", "dr5").
    RuntimeError
        If the Gaia query job does not complete successfully or if there is an
        error while fetching the query results.
    """

    def __init__(self, source_id: int | str, data_release: str = "dr3"):
        if (
            not isinstance(source_id, (int, str))
            or (isinstance(source_id, str) and not source_id.isdigit())
        ):
            raise TypeError("source_id must be an integer or string")

        valid_data_releases = {"dr1", "dr2", "edr3", "dr3", "dr4", "dr5"}
        if data_release not in valid_data_releases:
            raise ValueError(
                f"Invalid data release. Must be one of {valid_data_releases}"
            )

        self.source_id = source_id
        self.data_release = data_release

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
                f"Query to the {self.data_release} main table did not complete"
                f" successfully. Job status: {phase}."
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
        try:
            return self.job.get_results()
        except Exception as e:
            raise RuntimeError(
                f"Error occurred while fetching query results: {e}"
            )


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
                gaia{self.data_release}.gaia_source
            WHERE
                source_id = {self.source_id}
            """
        ).strip()

        return query
