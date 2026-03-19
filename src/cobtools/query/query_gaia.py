from astroquery.gaia import Gaia
from astroquery.utils.tap.model.job import Job
from abc import ABC, abstractmethod
from astropy.table import Table
from textwrap import dedent
from functools import cached_property


class SingleSourceQuery(ABC):
    """
    Abstract base class for querying the Gaia archive.

    This class defines the interface for querying the Gaia archive. Subclasses
    must implement the ``query_result`` method to specify how to query the
    archive for a specific ``source_id``.

    Attributes
    ----------
    source_id : int or str
        The ``source_id`` to query. Must be an integer or string of numbers.
    data_release : str
        The Gaia data release to use (default is "dr3"). Valid options are
        "dr1", "dr2", "edr3", "dr3", "dr4", and "dr5".

    Methods
    -------
    query_str() -> str
        Abstract property to return the ADQL query string for the specified
        ``source_id``.
    query_result() -> Table
        Abstract method to query the Gaia archive for a specific ``source_id``.
    """

    def __init__(self, source_id: int | str, data_release: str = "dr3"):
        if not isinstance(source_id, (int, str)):
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

    @abstractmethod
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
    Implementation of SingleSourceQuery for querying the Gaia archive,
    returning the full set of columns for a given source_id.

    Methods
    -------
    query_str() -> str
        Return the ADQL query string to retrieve all columns for the specified
        ``source_id``.
    query_result() -> Table
        Query the Gaia archive for a specific ``source_id`` and return the
        results as an ``astropy.table.Table object``.
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
