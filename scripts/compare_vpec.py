import pandas as pd
import matplotlib.pyplot as plt
from cobtools.astrometry.kinematics import peculiar_velocity


def compare_vpec() -> None:
    df = pd.read_csv("./test_data/zhao23_catalogue.csv")

    ra = df["ra_gaia"].values
    dec = df["dec_gaia"].values
    pmra = df["pmra"].values
    pmdec = df["pmdec"].values
    dist = df["d_exp"].values
    rv = df["v_r"].values

    results = peculiar_velocity(
        ra, dec, pmra, pmdec, dist, rv
    )

    vpec_expected = df["vpec"].values
    vpec_loerr = df["e_vpec"].values
    vpec_hierr = df["E_vpec"].values
    vpec_avg_err = (vpec_loerr + vpec_hierr) / 2

    vpec_cobtools = results[-1]
    df["vpec_cobtools"] = vpec_cobtools

    discrepancies = (vpec_cobtools - vpec_expected) / vpec_avg_err

    df_different = df[abs(discrepancies) > 1]
    print(f"Found {len(df_different)} stars with discrepancies > 1 sigma:")
    print(
        df_different[["ID_short", "vpec", "vpec_cobtools", "e_vpec", "E_vpec"]]
    )

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.errorbar(
        vpec_expected, vpec_cobtools, yerr=[vpec_loerr, vpec_hierr],
        marker="o", alpha=0.5, linestyle="none", mfc="r", mec="k",
        ecolor="gray", elinewidth=0.5, capsize=2
    )

    ax.set_xlabel("vpec (Zhao+23)")
    ax.set_ylabel("vpec (cobtools)")

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlim(1, 600)
    ax.set_ylim(1, 600)

    xmin, xmax = ax.get_xlim()
    ax.plot([xmin, xmax], [xmin, xmax], color="k", linestyle="--")

    plt.savefig("./figures/vpec_comparison.pdf")


if __name__ == "__main__":
    compare_vpec()
