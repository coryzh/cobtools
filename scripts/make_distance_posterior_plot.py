
from cobtools.astrometry.distance import XRBExponentialPriorModel
import matplotlib.pyplot as plt
from pathlib import Path


def plot_distance_samples() -> None:
    model = XRBExponentialPriorModel(parallax=0.5, parallax_error=0.1)
    samples = model.sample_distance(nwalkers=10, nsteps=500, burn_in=100)

    _ = plt.hist(
        samples, bins=50, density=True, label=f"{len(samples)} samples"
    )

    plt.axvline(
        1 / model.parallax, color="red", linestyle="--", label="1/parallax"
    )
    plt.xlabel("Distance (kpc)")
    plt.ylabel("Probability Density")
    plt.text(
        0.5, 0.8,
        f"Parallax: {model.parallax} mas\n"
        f"Parallax Error: {model.parallax_error} mas\n"
        f"Scale Length: {model.scale_length} kpc",
        fontsize=10,
        transform=plt.gca().transAxes,
    )
    plt.legend()
    out_path = (
        Path().cwd() / "figures" / "test_exponential_distance_samples.pdf"
    )
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
