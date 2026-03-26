import click
import math
from cobtools.query.query_gaia import SingleSourceUsefulInfoQuery
from cobtools.photometry.color_index import bp_rp_to_sptype
from astropy.table import Table


@click.command()
@click.argument("source_id", type=int)
@click.option(
    "--dr", "-r",
    default="dr3",
    show_default=True,
    help=(
        "Gaia data release to query. Valid options are 'dr2', 'edr3', 'dr3', "
        "'dr4', and 'dr5'."
    )
)
def query_useful_info(source_id: int, dr: str):
    """
    Query useful information about a Gaia source.

    This command retrieves a subset of useful columns from the Gaia archive
    for the specified SOURCE_ID and displays the results in a formatted table.

    Parameters
    ----------
    source_id : int
        The Gaia source identifier.
    dr : str
        The Gaia data release to query.
    """

    try:
        query = SingleSourceUsefulInfoQuery(
            source_id=source_id, data_release=dr
        )
        result: Table = query.query_result()
        if len(result) == 0:
            click.echo(f"No results found for SOURCE_ID {source_id} in {dr}.")
            return
        else:
            display_result(result)

    except ValueError as e:
        click.echo(f"Error: {e}")
        return
    except RuntimeError as e:
        click.echo(f"Runtime error: {e}")
        return
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")
        return


def styled_title(title):
    return click.style(title, fg="cyan", bold=True)


def get_spectral_type(bp_rp: float, kind: str, mh: float = 0.0):
    """
    Get the spectral type for a given BP-RP value and kind (dwarf/giant).

    Parameters
    ----------
    bp_rp : float
        The BP-RP color index.
    kind : str
        The kind of star ("dwarf" or "giant").
    mh : float, optional
        The metallicity, by default 0.0 (solar metallicity).

    Returns
    -------
    str
        The spectral type string, or "NA (kind)" if an error occurs.
    """
    try:
        sptype = bp_rp_to_sptype(bp_rp=bp_rp, mh=mh, kind=kind)
        return f"{sptype} ({kind})"
    except ValueError:
        return f"NA ({kind})"


def display_result(result: Table) -> None:
    """
    Display the query result in a formatted table.

    Parameters
    ----------
    result : Table
        The query result to display.
    """

    df = result.to_pandas()
    row = df.iloc[0]

    ra = row["ra"]
    dec = row["dec"]
    gal_l = row["l"]
    gal_b = row["b"]
    parallax = row["parallax"]
    parallax_error = row["parallax_error"]
    pmra = row["pmra"]
    pmra_error = row["pmra_error"]
    pmdec = row["pmdec"]
    pmdec_error = row["pmdec_error"]
    rv = row["radial_velocity"]
    rv_error = row["radial_velocity_error"]
    aen = row["astrometric_excess_noise"]
    aen_sig = row["astrometric_excess_noise_sig"]
    gmag = row["phot_g_mean_mag"]
    bp_rp = row["bp_rp"]
    mh = row["mh_gspphot"]

    mh_for_sptype = mh if not math.isnan(mh) else 0.0

    ag_gspphot = row["ag_gspphot"]
    ebpminrp_gspphot = row["ebpminrp_gspphot"]

    in_qso = row["in_qso_candidates"]
    in_galaxy = row["in_galaxy_candidates"]

    has_xp_continuous = row["has_xp_continuous"]
    has_epoch_rv = row["has_epoch_rv"]
    has_rvs = row["has_rvs"]
    nss = row["non_single_star"]
    has_epoch_photometry = row["has_epoch_photometry"]

    sptype_dwarf_str = get_spectral_type(
        bp_rp=bp_rp, kind="dwarf", mh=mh_for_sptype
    )
    sptype_giant_str = get_spectral_type(
        bp_rp=bp_rp, kind="giant", mh=mh_for_sptype
    )

    sptype_str = f"{sptype_dwarf_str} / {sptype_giant_str}"

    ra_dec_str = f"{ra}, {dec}"
    gal_l_b_str = f"{gal_l}, {gal_b}"
    parallax_str = f"{parallax:.4f} ± {parallax_error:.4f} mas"
    pmra_str = f"{pmra:.4f} ± {pmra_error:.4f} mas/yr"
    pmdec_str = f"{pmdec:.4f} ± {pmdec_error:.4f} mas/yr"
    rv_str = f"{rv:.2f} ± {rv_error:.2f} km/s"
    aen_str = f"{aen:.4f} ({aen_sig:.4f}) mas"
    ruwe_str = f"{row['ruwe']:.3f}"
    gmag_str = f"{gmag:.3f}"
    ag_str = f"{ag_gspphot:.3f}"
    bp_rp_str = f"{bp_rp:.3f}"
    e_bpminrp_str = f"{ebpminrp_gspphot:.3f}"
    mh_str = f"{mh:.3f}"

    in_qso_str = f"{'True' if in_qso else 'False'}"

    in_galaxy_str = f"{'True' if in_galaxy else 'False'}"

    has_xp_spectrum = f"{'True' if has_xp_continuous else 'False'}"
    has_rvs_spectrum = f"{'True' if has_rvs else 'False'}"
    has_epoch_rv_str = f"{'True' if has_epoch_rv else 'False'}"
    has_epoch_photometry_str = f"{'True' if has_epoch_photometry else 'False'}"

    # Define a width for alignment
    title_width = 30

    # Format rows with alignment
    output_lines = [
        f"{styled_title('ra, dec'):<{title_width}}: {ra_dec_str}",
        f"{styled_title('l, b'):<{title_width}}: {gal_l_b_str}",
        f"{styled_title('parallax'):<{title_width}}: {parallax_str}",
        f"{styled_title('pmra_cosdec'):<{title_width}}: {pmra_str}",
        f"{styled_title('pmdec'):<{title_width}}: {pmdec_str}",
        f"{styled_title('rv'):<{title_width}}: {rv_str}",
        f"{styled_title('aen (sig)'):<{title_width}}: {aen_str}",
        f"{styled_title('ruwe'):<{title_width}}: {ruwe_str}",
        f"{styled_title('g mag'):<{title_width}}: {gmag_str}",
        f"{styled_title('A_G'):<{title_width}}: {ag_str}",
        f"{styled_title('bp-rp'):<{title_width}}: {bp_rp_str}",
        f"{styled_title('E(BP-RP)'):<{title_width}}: {e_bpminrp_str}",
        f"{styled_title('sptype'):<{title_width}}: {sptype_str}",
        f"{styled_title('mh'):<{title_width}}: {mh_str}",
        f"{styled_title('galaxy candidates'):<{title_width}}: {in_galaxy_str}",
        f"{styled_title('qso candidates'):<{title_width}}: {in_qso_str}",
        f"{styled_title('xp spectra'):<{title_width}}: {has_xp_spectrum}",
        f"{styled_title('rvs spectrum'):<{title_width}}: {has_rvs_spectrum}",
        f"{styled_title('epoch rvs'):<{title_width}}: {has_epoch_rv_str}",
        (
            f"{styled_title('epoch photometry'):<{title_width}}: "
            f"{has_epoch_photometry_str}"
        ),
        (
            f"{styled_title('non-single star'):<{title_width}}: "
            f"{'True' if nss else 'False'}"
        )
    ]
    click.echo("\n".join(output_lines))


if __name__ == "__main__":
    query_useful_info()
