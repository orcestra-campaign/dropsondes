# %%
import matplotlib.pyplot as plt
import seaborn as sns
import xhistogram.xarray as xh
import xarray as xr
import numpy as np

# %%

root = "ipfs://Qmbx6KSDfviFFi7f5XXQLB6MSTPhWnN1rNkCCKhyhaa7CA"
ds = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3_qc/PERCUSION_Level_3.zarr", engine="zarr"
)

# %%
colors = ["#689F38", "#1976D2", "#FFA000", "#7B1FA2"]

nb_bins = 50
variables = ["u", "rh", "ta", "p"]
bins_fullness = np.linspace(0, 1, nb_bins)
bins_count = np.linspace(0, 210, nb_bins)
bins_extend = np.linspace(0, 1, nb_bins)
var = variables[0]

fig, axes = plt.subplots(ncols=3, figsize=(18, 6))
for var, color in zip(variables, colors):
    h_fullness = xh.histogram(
        ds[var + "_profile_fullness_fraction"], bins=[bins_fullness]
    )
    h_fullness.plot(ax=axes[0], color=color, label=var)
    h_count = xh.histogram(ds[var + "_near_surface_count"], bins=[bins_count])
    h_count.plot(ax=axes[1], color=color, label=var)
    ext = ds[var + "_profile_extend_max_diff"] / ds["aircraft_msl_altitude"]
    ext.name = "extend"
    h_extend = xh.histogram(ext, bins=[bins_extend])
    h_extend.plot(ax=axes[2], color=color, label=var)
ax = axes[0]
ax.set_xlabel("Profile Fullness Fraction")
ax.set_ylabel("Number of Sondes")
ax.set_xlim(0.5, 1)
ax.legend()
ax.axvline(0.8, color="gray", alpha=0.5)
ax = axes[1]
ax.set_ylabel("")
ax.set_xlabel("Number of Near-Surface Measurements")
ax.axvline(50, color="gray", alpha=0.5)
ax.legend()
ax = axes[2]
ax.set_ylabel("")
ax.set_xlabel("(aircraft_msl_altitude - profile_max) / aircraft_msl_altitude")
ax.legend()
ax.axvline(0.2, color="gray", alpha=0.5)
ax.set_xlim(0, 0.5)
sns.despine(offset=10)
fig.savefig(
    "../images/qc_distribution.png",
)
