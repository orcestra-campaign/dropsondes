# %%

import numpy as np
import xarray as xr
import seaborn as sns
import matplotlib.pyplot as plt
import settings
import droputils.data_utils as du

lev3 = xr.open_dataset(
    f"ipfs://{settings.lev3}",
    engine="zarr",
)
lev2 = xr.open_dataset(
    f"ipfs://{settings.lev2}",
    engine="zarr",
)

# %% takes some time
values = []
pvalues = []
for idx, sonde in enumerate(lev3.sonde_id.values):
    sondeidx = list(lev2.sonde_id.values).index(sonde)
    ds = du.sel_sonde(lev2, sondeidx)

    values.append(ds.gpsalt.dropna("time").values[0])
    pvalues.append(ds.p.dropna("time").values[0])
# %%
sns.set_context("paper", font_scale=0.8)
plt.style.use("./beach.mplstyle")
constrained_alt = np.where(np.abs(values) < 100, values, np.nan)
constrained_p = np.where(np.array(pvalues) > 100500, pvalues, np.nan)
constrained_p[constrained_p > 102000] = np.nan
cm = 1 / 2.54
fig, ax1 = plt.subplots(figsize=(8.3 * cm, 8.3 * cm))

altrange = (np.nanmean(constrained_alt) - 50, np.nanmean(constrained_alt) + 50)
sns.histplot(
    constrained_alt,
    bins=50,
    binrange=(2.4 - 50, 2.4 + 50),
    stat="probability",
    alpha=0.5,
    color="C0",
    kde=True,
    element="step",
    ax=ax1,
)
ax2 = ax1.twiny()

p_range = (np.nanmean(constrained_p) - 500, np.nanmean(constrained_p) + 500)
sns.histplot(
    constrained_p,
    bins=50,
    binrange=p_range,
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
ax1.set_xlim(altrange)
ax2.set_xlim(p_range)
ax1.set_xlabel("last gpsalt value / m")
ax2.set_xlabel("last pressure value / Pa")
# axes[1].set_ylabel("")

sns.despine(offset={"left": 5})
fig.savefig("../images/surface_hist.pdf", bbox_inches="tight")
