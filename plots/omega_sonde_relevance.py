# %%

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
import cmocean as cmo  # noqa
from xhistogram.xarray import histogram
import settings
from droputils import data_utils as du


# %%
lev4 = xr.open_dataset(
    f"{settings.root}/products/HALO/dropsondes/Level_4/PERCUSION_Level_4.zarr",
    engine="zarr",
)

# %%

spc = du.get_circle_id_for_sondes(lev4)
spc = spc.assign(
    omega_sonde=(
        ("sonde", "altitude"),
        np.concat(
            [
                np.stack(
                    ([spc.sel(circle=circle).omega.values],)
                    * int(spc.sel(circle=circle).sondes_per_circle.values),
                    axis=0,
                ).squeeze()
                for circle in spc.circle
            ],
            axis=0,
        ),
    ),
)

# %%
plt_var = "omega_sonde_relevance"  # "rel_error"  #
cm = 1 / 2.54

plt.style.use("./beach.mplstyle")
sns.set_palette("bright")
err = lev4.omega_sonde_relevance * 0.01 * (60 * 60)
binsize = 50
sig_om_err = err  # .where(original_values > 1)
# sig_om_err = (err / spc.omega_sonde.where(spc.omega_sonde != 0)).rename("rel_error")
bins_div = np.linspace(
    sig_om_err.min().values, sig_om_err.max().values, binsize
)  # -2 to 2

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
    # vmax=100,
    ax=axes[1, 0],
    add_colorbar=False,
    rasterized=True,
    y="altitude_bin",
)
for ax in axes[:, 0]:
    (-2 * lev4.omega_sonde_relevance.std("sonde") * 0.01 * (60 * 60)).sel(
        altitude=slice(0, 13500)
    ).plot(y="altitude", zorder=10, ax=axes[1, 0], color="k", linewidth=0.5)
    (2 * lev4.omega_sonde_relevance.std("sonde") * 0.01 * (60 * 60)).sel(
        altitude=slice(0, 13500)
    ).plot(y="altitude", zorder=10, ax=axes[1, 0], color="k", linewidth=0.5)

axes[1, 0].annotate(
    r"-2 $\sigma$",
    xy=(-3.2, 14500),
    xytext=(-3.2, 14500),
    fontsize=5,
    # rotation=270,
    ha="right",
    va="bottom",
)
axes[1, 0].annotate(
    r"2 $\sigma$",
    xy=(3.2, 14500),
    xytext=(3.2, 14500),
    fontsize=5,
    # rotation=270,
    ha="left",
    va="bottom",
)


axes[1, 0].set_ylabel("altitude / m")
axes[1, 0].set_xlabel(r"$\Delta \omega$ / hPa hr-1" + "\n if sonde is removed ")

sns.histplot(
    sig_om_err.to_dataframe()[plt_var]
    .reset_index()
    .drop("altitude", axis=1)
    .drop("sonde", axis=1),
    bins=200,
    binrange=(-10, 10),
    stat="probability",
    alpha=0.5,
    color="#00267f",
    kde=True,
    legend=False,
    element="step",
    ax=axes[0, 0],
)
axes[0, 0].set_ylabel("")
sns.despine(offset={"left": 5})

cbaxes = axes[1, 0].inset_axes((0.73, 0.04, 0.04, 0.3))
cbar = fig.colorbar(
    im,
    cax=cbaxes,
    orientation="vertical",
    fraction=1,
    # extend="max",
)
cbar.ax.tick_params(pad=0.2, length=2)
cbar.set_label("count", size=5, labelpad=1)
cbar.ax.tick_params(labelsize=5)

xticks = [-10, 0, 10]
xticks.append(-2 * sig_om_err.std().values)
xticks.append(2 * sig_om_err.std().values)

axes[1, 0].set_xticks(
    xticks, labels=xticks[:-2] + ["{:.2f}".format(x) for x in xticks[-2:]]
)

# error measure
sonde_idx = np.insert(np.cumsum(lev4.sondes_per_circle), 0, 0)

circles = [13, 23, 28, 31, 54, 80, 87]
for circle in circles:
    ds = lev4.sel(circle=circle)
    sonde_ds = lev4.sel(
        sonde=slice(sonde_idx[circle].values, sonde_idx[circle + 1].values)
    )
    for ax in axes[1, 1:]:
        omega = ds.omega * 0.01 * (60 * 60)
        omega_std = ds.omega_std_error * 0.01 * (60 * 60)
        omega.plot(y="altitude", ax=ax, label=ds.circle_id.values)
    axes[1, 1].fill_betweenx(
        ds.altitude,
        omega - omega_std,
        omega + omega_std,
        alpha=0.2,
    )

    axes[1, 2].fill_betweenx(
        ds.altitude,
        omega + (sonde_ds.omega_sonde_relevance * 0.01 * (60 * 60)).min(),
        omega + (sonde_ds.omega_sonde_relevance * 0.01 * (60 * 60)).max(),
        alpha=0.2,
    )
for ax in axes[1, 1:]:
    ax.set_ylabel("")
    ax.set_xlabel(r"$\omega$ / hPa hr-1")
axes[1, 1].set_title("Regression Standard Error", fontsize=7)
axes[1, 2].set_title("Sonde Relevance", fontsize=7)
axes[1, 1].legend(loc=2, fontsize=3)
for ax in axes[0, 1:]:
    ax.set_axis_off()

fig.savefig("../images/omega_error_2d.pdf", dpi=300, bbox_inches="tight")

# %%
(lev4.omega_sonde_relevance.std("sonde") * 0.01 * (60 * 60)).sel(
    altitude=slice(0, 14000)
).mean()
