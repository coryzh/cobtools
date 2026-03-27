#!/usr/bin/env python3

import click


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Retrieve and display a subset of columns about a Gaia source.\n\n"
         "This command queries the Gaia archive for the specified source_id "
         "and data release (--dr), and displays the results in a formatted "
         "table."
)
@click.argument(
    "source_id", type=int, metavar="source_id"
)
@click.option(
    "--dr",
    default="dr3",
    show_default=True,
    type=str,
    metavar="Data Release",
    help=(
        "Gaia data release to query. Current valid options are 'dr2', 'edr3',"
        " and 'dr3'. This will be extended to include 'dr4', and 'dr5'."
    ),
)
def query_useful_info(source_id: int, dr: str):
    """
    Retrieve useful information about a Gaia source.

    Queries the Gaia archive for the specified source_id and data release
    (--dr), and displays the results in a formatted table.
    """
    from cobtools.query.query_gaia import SingleSourceUsefulInfoQuery

    try:
        query = SingleSourceUsefulInfoQuery(
            source_id=source_id, data_release=dr
        )
        result = query.query_result()
        if len(result) == 0:
            click.echo(f"No results found for {source_id} in {dr}.")
            return

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


def styled_title(title, width=30):
    return click.style(f"{title:<{width}}", fg="cyan", bold=True)


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
    from cobtools.photometry.color_index import bp_rp_to_sptype

    try:
        sptype = bp_rp_to_sptype(bp_rp=bp_rp, mh=mh, kind=kind)
        return f"{sptype} ({kind})"
    except ValueError:
        return f"NA ({kind})"


def display_result(result) -> None:
    """
    Display the query in a formatted table.

    Parameters
    ----------
    result : Table
        The query result to display.
    """

    import pandas as pd

    df = result.to_pandas()
    row = df.iloc[0]

    bp_rp = row["bp_rp"]
    mh = row["mh_gspphot"]
    mh_for_sptype = mh if not pd.isna(mh) else 0.0

    sptype_dwarf_str = get_spectral_type(
        bp_rp=bp_rp, kind="dwarf", mh=mh_for_sptype
    )
    sptype_giant_str = get_spectral_type(
        bp_rp=bp_rp, kind="giant", mh=mh_for_sptype
    )

    def fmt_bool(val):
        if pd.isna(val):
            return "False"
        return "True" if bool(val) else "False"

    title_width = 17
    rows = [
        ("source_id", f"{row['source_id']}"),
        ("ra, dec", f"{row['ra']}, {row['dec']}"),
        ("l, b", f"{row['l']}, {row['b']}"),
        (
            "parallax",
            f"{row['parallax']:.4f} ± {row['parallax_error']:.4f} mas",
        ),
        ("pmra_cosdec", f"{row['pmra']:.4f} ± {row['pmra_error']:.4f} mas/yr"),
        ("pmdec", f"{row['pmdec']:.4f} ± {row['pmdec_error']:.4f} mas/yr"),
        (
            "rv",
            (
                f"{row['radial_velocity']:.2f} "
                f"± {row['radial_velocity_error']:.2f} km/s"
                if not pd.isna(row['radial_velocity'])
                and not pd.isna(row['radial_velocity_error'])
                else "nan"
            )
        ),
        (
            "aen (sig)",
            (
                f"{row['astrometric_excess_noise']:.4f} "
                f"({row['astrometric_excess_noise_sig']:.4f}) mas"
            ),
        ),
        ("ruwe", f"{row['ruwe']:.3f}"),
        ("g mag", f"{row['phot_g_mean_mag']:.3f}"),
        ("A_G", f"{row['ag_gspphot']:.3f}"),
        ("bp-rp", f"{bp_rp:.3f}"),
        ("E(BP-RP)", f"{row['ebpminrp_gspphot']:.3f}"),
        ("sptype", f"{sptype_dwarf_str} / {sptype_giant_str}"),
        ("mh", f"{mh:.3f}"),
        ("galaxy candidates", fmt_bool(row["in_galaxy_candidates"])),
        ("qso candidates", fmt_bool(row["in_qso_candidates"])),
        ("xp spectra", fmt_bool(row["has_xp_continuous"])),
        ("rvs spectrum", fmt_bool(row["has_rvs"])),
        ("epoch rvs", fmt_bool(row["has_epoch_rv"])),
        ("epoch photometry", fmt_bool(row["has_epoch_photometry"])),
        ("non-single star", fmt_bool(row["non_single_star"])),
    ]

    output_lines = [
        f"{styled_title(label, title_width)}: {value}"
        for label, value in rows
    ]
    click.echo("\n".join(output_lines))


if __name__ == "__main__":
    query_useful_info()
