# %%

import numpy as np
import xarray as xr
import seaborn as sns
import matplotlib.pyplot as plt
import settings

lev3 = xr.open_dataset(
    f"{settings.root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr",
    engine="zarr",
)
# %%
values = []
pvalues = []
for idx, sonde in enumerate(lev3.sonde_id.values):
    fid = lev3.where(lev3.sonde_id == sonde, drop=True).flight_id.values[0]
    path = f"{settings.root}/products/HALO/dropsondes/Level_2/{fid}/PERCUSION_{sonde}_Level_2.zarr"
    l2_ds = (
        xr.open_dataset(path, engine="zarr")
        .sortby("time", ascending=False)
        .dropna(dim="time", subset=["gpsalt"])
    )
    values.append(l2_ds.gpsalt.values[0])
    pvalues.append(l2_ds.p.values[0])
# %%
plt.style.use("./beach.mplstyle")
constrained_alt = np.where(np.abs(values) < 100, values, np.nan)
constrained_p = np.where(np.array(pvalues) > 100500, pvalues, np.nan)
constrained_p[constrained_p > 102000] = np.nan

fig, ax1 = plt.subplots(figsize=(6, 6))


sns.histplot(
    constrained_alt,
    bins=200,
    stat="probability",
    alpha=0.5,
    color="C0",
    kde=True,
    element="step",
    ax=ax1,
)
ax2 = ax1.twiny()

sns.histplot(
    constrained_p,
    bins=100,
    stat="probability",
    alpha=0.5,
    color="C1",
    kde=True,
    element="step",
    ax=ax2,
)
for ax, c in zip([ax1, ax2], ["C0", "C1"]):
    ax.set_title("")

    ax.xaxis.label.set_color(c)
    ax.tick_params(axis="x", colors=c)
ax2.spines["bottom"].set_color("C0")

# ax.axvline(0, c="gray")
ax1.set_xlim(-50, 50)
ax2.set_xlim(100470, 101470)
ax1.set_xlabel("last gpsalt value / m")
ax2.set_xlabel("last pressure value / Pa")
# axes[1].set_ylabel("")

sns.despine(offset={"left": 10})
fig.tight_layout()
fig.savefig("../images/surface_hist.pdf")
