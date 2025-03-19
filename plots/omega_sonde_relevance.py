# %%

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
import cmocean as cmo  # noqa
from xhistogram.xarray import histogram
import settings
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


# %%
lev4 = xr.open_dataset(
    f"{settings.root}/products/HALO/dropsondes/Level_4/PERCUSION_Level_4.zarr",
    engine="zarr",
)

# %%
plt.style.use("./beach.mplstyle")
err = lev4.omega_sonde_relevance
binsize = 200
sig_om_err = err  # .where(original_values > 1)
bins_div = np.linspace(sig_om_err.min().values, sig_om_err.max().values, binsize)
fig, axes = plt.subplots(nrows=2, height_ratios=(0.3, 2), sharex=True, figsize=(6, 6.9))

hist = histogram(sig_om_err, sig_om_err.altitude, bins=[bins_div, binsize])
im = hist.where(hist != 0).plot(
    cmap="cmo.ice_r",
    vmin=0,
    vmax=100,
    ax=axes[1],
    add_colorbar=False,
    y="altitude_bin",
)
cbaxes = inset_axes(axes[1], width="3%", height="30%", loc=4)
fig.colorbar(
    im, cax=cbaxes, orientation="vertical", label="count", fraction=1, extend="max"
)

axes[1].set_ylabel("altitude / m")
axes[1].set_xlabel("difference in omega if sonde is removed / hPa hr-1")

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
    ax=axes[0],
)
axes[0].set_ylabel("")
sns.despine(offset={"left": 10})
fig.tight_layout()

fig.savefig("../images/omega_error_2d.png")
# %%
plt.style.use("./beach.mplstyle")

sonde_idx = np.insert(np.cumsum(lev4.sondes_per_circle), 0, 0)
sns.set_palette("bright")
circles = [13, 23, 28, 31, 54, 80, 87]
fig, axes = plt.subplots(ncols=2, figsize=(12, 6), sharey=True, sharex=True)
for circle in circles:
    ds = lev4.sel(circle=circle)
    sonde_ds = lev4.sel(
        sonde=slice(sonde_idx[circle].values, sonde_idx[circle + 1].values)
    )
    for ax in axes:
        ds.omega.plot(y="altitude", ax=ax, label=ds.circle_id.values)
    axes[0].fill_betweenx(
        ds.altitude,
        ds.omega - ds.omega_std_error,
        ds.omega + ds.omega_std_error,
        alpha=0.2,
    )

    axes[1].fill_betweenx(
        ds.altitude,
        ds.omega + sonde_ds.omega_sonde_relevance.min(),
        ds.omega + sonde_ds.omega_sonde_relevance.max(),
        alpha=0.2,
    )
axes[1].set_ylabel("")
axes[0].set_title("Regression Standard Error")
axes[1].set_title("Sonde Relevance for Circle")
for ax in axes:
    ax.set_xlabel("omega / hPa hr-1")
axes[0].legend(fontsize=12, loc=2)
sns.despine(offset={"left": 10})
fig.savefig("../images/error_meassures.pdf", bbox_inches="tight")
