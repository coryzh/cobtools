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
        The source_id to query. Accepts an integer, or any value convertible to
        integer by Python `int(...)` semantics (for example, strings with
        surrounding whitespace or a leading +). Float inputs are rejected.

    data_release : str
        The Gaia data release to use.

    Attributes
    ----------
    source_id_obj : SourceID
        A SourceID object that encapsulates the source_id and data_release
        information.

    Properties
    ----------
    source_id : int
        Read-only. The numeric Gaia ``source_id``. Forwards to
        ``self.source_id_obj.source_id``.

        :noindex:

    data_release : str
        Read-only. The Gaia data release string (e.g. ``"dr3"``). Forwards to
        ``self.source_id_obj.data_release``.

        :noindex:

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
    def source_id(self) -> int:
        """
        Backwards-compatible access to the numeric Gaia ``source_id``.

        This read-only property forwards to ``self.source_id_obj.source_id``.

        Returns
        -------
        int
            The Gaia source identifier.
        """
        return self.source_id_obj.source_id

    @property
    def data_release(self) -> str:
        """
        Backwards-compatible access to the Gaia ``data_release`` string.

        This read-only property forwards to
        ``self.source_id_obj.data_release``.

        Returns
        -------
        str
            The Gaia data release (e.g. ``"dr3"``).
        """
        return self.source_id_obj.data_release

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
        if phase != "COMPLETED":
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
        query = dedent(f"""
            SELECT
                *
            FROM
                gaia{self.source_id_obj.data_release}.gaia_source
            WHERE
                source_id = {self.source_id_obj.source_id}
            """).strip()

        return query


class SingleSourceUsefulInfoQuery(SingleSourceQuery):
    """
    Concrete implementation of SingleSourceQuery for querying a subset of
    useful columns from the Gaia main table.

    Parameters
    ----------
    source_id : str or int
        The source_id to query. See `SourceID` for valid formats.

    data_release : str
        The Gaia data release to query. See `SourceID` for valid options.

    Properties
    ----------
    query_str : str
        The ADQL query string to retrieve a specific subset of useful columns
        for the specified ``source_id`` from the Gaia main table.
    """
    _COLUMN_SETS = {
        "dr1": [
            "source_id", "ra", "dec", "l", "b", "phot_g_mean_mag", "parallax",
            "parallax_error", "pmra", "pmra_error", "pmdec", "pmdec_error"
        ],

        "dr2": [
            "source_id", "ra", "dec", "l", "b", "phot_g_mean_mag", "parallax",
            "parallax_error", "pmra", "pmra_error", "pmdec", "pmdec_error",
            "radial_velocity", "radial_velocity_error", "bp_rp"
        ],
        "dr3": [
                "source_id", "ra", "dec", "l", "b", "phot_g_mean_mag",
                "parallax", "parallax_error", "pmra", "pmra_error", "pmdec",
                "pmdec_error", "radial_velocity", "radial_velocity_error",
                "ruwe", "astrometric_excess_noise",
                "astrometric_excess_noise_sig", "bp_rp", "non_single_star",
                "mh_gspphot", "ag_gspphot", "ebpminrp_gspphot",
                "in_qso_candidates", "in_galaxy_candidates",
                "has_xp_continuous", "has_epoch_photometry", "has_rvs",
                "has_epoch_rv"
        ]
    }

    def __init__(self, source_id: int | str, data_release: str = "dr3"):
        if data_release not in self._COLUMN_SETS:
            raise ValueError(
                f"Unsupported data_release: {data_release} for "
                "single-source useful info query. Valid options are: "
                f"{', '.join(self._COLUMN_SETS.keys())}."
            )
        super().__init__(source_id, data_release)

    @property
    def query_str(self) -> str:
        columns = self._COLUMN_SETS.get(self.data_release)
        query = dedent(f"""
            SELECT
                {", ".join(columns)}
            FROM gaia{self.source_id_obj.data_release}.gaia_source
            WHERE source_id = {self.source_id_obj.source_id}
            """).strip()

        return query


class SingleSourceNSSQuery(SingleSourceQuery):
    """
    Concrete implementation of SingleSourceQuery for querying the Gaia
    Non-Single Star (NSS) catalogs.

    This class retrieves all columns for a given ``source_id`` from the
    specified NSS catalog. Currently, `data_release` is restricted to "dr3"
    since the NSS catalogs are only available in DR3.

    Parameters
    ----------
    source_id : str or int
        The source_id to query.

    data_release : str
        Must be "dr3" for NSS queries since the NSS catalogs are only available
        in DR3.

    table_name : str
        The specific NSS catalog table to query. Valid options are:
        - "nss_two_body_orbit"
        - "nss_acceleration"
        - "nss_non_linear_spectro"

    Methods
    ----------
    query_str : str
        The ADQL query string to retrieve all columns for the specified
        ``source_id`` from the Gaia NSS catalog.
    """

    _VALID_TABLES = [
        "nss_two_body_orbit", "nss_acceleration", "nss_non_linear_spectro"
    ]

    def __init__(
        self,
        source_id: int | str,
        data_release: str = "dr3",
        table_name: str = "nss_two_body_orbit",
    ):
        if data_release != "dr3":
            raise ValueError(
                "Currently, only data_release='dr3' is supported "
                "for NSS queries since the NSS catalogs are only "
                "available in DR3."
            )
        if table_name not in self._VALID_TABLES:
            raise ValueError(
                f"Invalid table_name: {table_name}. "
                f"Valid options are: {', '.join(self._VALID_TABLES)}."
            )

        super().__init__(source_id, data_release)
        self.table_name = table_name

    @property
    def query_str(self) -> str:
        """
        The ADQL query to retrieve all columns for a given source_id from the
        Gaia NSS catalog.

        Returns
        -------
        str
            The ADQL query string.
        """
        query = dedent(f"""
            SELECT
                *
            FROM
                gaia{self.source_id_obj.data_release}.{self.table_name}
            WHERE
                source_id = {self.source_id_obj.source_id}
            """).strip()

        return query

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
        if phase != "COMPLETED":
            raise RuntimeError(
                f"Query to the {self.source_id_obj.data_release} NSS table "
                f"'{self.table_name}' did not complete successfully. "
                f"Job status: {phase}."
            )
        return job
