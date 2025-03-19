# %%
import matplotlib.pyplot as plt
import seaborn as sns
import xarray as xr
import numpy as np
import settings

# %%
ds = xr.open_dataset(
    f"{settings.root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3_qc.zarr",
    engine="zarr",
)

# %%


colors = ["C2", "C0", "C1", "C2", "C3"]

nb_bins = 50
variables = ["u", "rh", "ta"]  # , "p"]
bins_fullness = np.linspace(0, 1, nb_bins)
bins_count = np.linspace(0, 210, nb_bins)
bins_extend = np.linspace(0, 15000, nb_bins)
var = variables[0]

plt.style.use("./beach.mplstyle")
fig, axes = plt.subplots(ncols=3, figsize=(18, 6))
for var, color in zip(variables, colors):
    sns.histplot(
        ds[var + "_profile_sparsity_fraction"],
        alpha=0.5,
        stat="probability",
        kde=True,
        element="step",
        ax=axes[0],
        color=color,
    )
    sns.histplot(
        ds[var + "_near_surface_count"],
        alpha=0.5,
        stat="probability",
        kde=True,
        element="step",
        ax=axes[1],
        color=color,
    )
    sns.histplot(
        ds[var + "_profile_extent_max"],
        alpha=0.5,
        stat="probability",
        bins=200,
        element="step",
        ax=axes[2],
        color=color,
    )

ax = axes[0]
ax.set_xlabel("Profile Sparsity Fraction")
ax.set_ylabel("")
ax.set_xlim(0, 0.5)
ax.legend()
ax.axvline(0.2, color="gray", alpha=0.5)
ax = axes[1]
ax.set_ylabel("")
ax.set_xlabel("# Near-Surface Measurements")
ax.axvline(50, color="gray", alpha=0.5)
ax.legend()
ax = axes[2]
ax.set_ylabel("")
ax.set_xlabel("Profile Extent / m")
ax.legend()
ax.axvline(8000, color="gray", alpha=0.5)
ax.set_xlim(0, 15500)
fig.savefig(
    "../images/qc_distribution.png",
)
