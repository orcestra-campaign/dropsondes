# %%

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
import cmocean as cmo  # noqa
from xhistogram.xarray import histogram
import settings


# %%
lev4 = xr.open_dataset(
    f"{settings.root}/products/HALO/dropsondes/Level_4/PERCUSION_Level_4.zarr",
    engine="zarr",
)

# %%
cm = 1 / 2.54
plt.style.use("./beach.mplstyle")
sns.set_palette("bright")
err = lev4.omega_sonde_relevance
binsize = 200
sig_om_err = err  # .where(original_values > 1)
bins_div = np.linspace(sig_om_err.min().values, sig_om_err.max().values, binsize)
fig, axes = plt.subplots(
    nrows=2,
    ncols=3,
    height_ratios=(0.3, 2),
    sharex="col",
    sharey="row",
    figsize=(12 * cm, 5.5 * cm),
)

hist = histogram(sig_om_err, sig_om_err.altitude, bins=[bins_div, binsize])
im = hist.where(hist != 0).plot(
    cmap="cmo.ice_r",
    vmin=0,
    vmax=100,
    ax=axes[1, 0],
    add_colorbar=False,
    rasterized=True,
    y="altitude_bin",
)

axes[1, 0].set_ylabel("altitude / m")
axes[1, 0].set_xlabel("difference in omega \n if sonde is removed / hPa hr-1")

sns.histplot(
    sig_om_err.to_dataframe()["omega_sonde_relevance"]
    .reset_index()
    .drop("altitude", axis=1)
    .drop("sonde", axis=1),
    bins=200,
    stat="probability",
    alpha=0.5,
    color="#00267f",
    kde=True,
    legend=False,
    element="step",
    ax=axes[0, 0],
)
axes[0, 0].set_ylabel("")
sns.despine(offset={"left": 10})

cbaxes = axes[1, 0].inset_axes((0.8, 0.03, 0.04, 0.3))
cbar = fig.colorbar(
    im,
    cax=cbaxes,
    orientation="vertical",
    fraction=1,
    extend="max",
)
cbar.ax.tick_params(pad=0.2, length=2)
cbar.set_label("count", size=4, labelpad=-1)

# error measure
sonde_idx = np.insert(np.cumsum(lev4.sondes_per_circle), 0, 0)

circles = [13, 23, 28, 31, 54, 80, 87]
for circle in circles:
    ds = lev4.sel(circle=circle)
    sonde_ds = lev4.sel(
        sonde=slice(sonde_idx[circle].values, sonde_idx[circle + 1].values)
    )
    for ax in axes[1, 1:]:
        ds.omega.plot(y="altitude", ax=ax, label=ds.circle_id.values)
    axes[1, 1].fill_betweenx(
        ds.altitude,
        ds.omega - ds.omega_std_error,
        ds.omega + ds.omega_std_error,
        alpha=0.2,
    )

    axes[1, 2].fill_betweenx(
        ds.altitude,
        ds.omega + sonde_ds.omega_sonde_relevance.min(),
        ds.omega + sonde_ds.omega_sonde_relevance.max(),
        alpha=0.2,
    )
for ax in axes[1, 1:]:
    ax.set_ylabel("")
    ax.set_xlabel("omega / hPa hr-1")
axes[1, 1].set_title("Regression Standard Error")
axes[1, 2].set_title("Sonde Relevance for Circle")
axes[1, 1].legend(loc=2, fontsize=3)
for ax in axes[0, 1:]:
    ax.set_axis_off()

fig.savefig("../images/omega_error_2d.pdf", dpi=300, bbox_inches="tight")
