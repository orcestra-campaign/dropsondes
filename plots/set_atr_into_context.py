# %%
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import settings
import seaborn as sns

from orcestra import get_flight_segments

# %% Load flight segments and select those with ATR coordination
meta = get_flight_segments()["HALO"]
segments = [
    {
        **s,
        "flight_id": flight_id,
    }
    for flight_id, flight in meta.items()
    for s in flight["segments"]
]

atr_circle_segments = [
    s for s in segments if "atr_coordination" in s["kinds"] and "circle" in s["kinds"]
]

# %% Load the dropsonde data
l3 = xr.open_dataset(
    f"ipfs://{settings.lev3}",
    engine="zarr",
).assign(wspd_sfc=lambda ds: ds.wspd.sel(altitude=slice(0, 51)).mean("altitude"))
l4 = xr.open_dataset(
    f"ipfs://{settings.lev4}",
    engine="zarr",
)

# Select the sondes related to ATR coordination
# %% Level 3
atr_times = [
    slice(s["start"], s["end"]) for s in segments if "atr_coordination" in s["kinds"]
]
ds_atr_list = [
    l3.swap_dims({"sonde": "launch_time"}).sel(launch_time=t) for t in atr_times
]
l3_atr = xr.concat(ds_atr_list, dim="launch_time").swap_dims({"launch_time": "sonde"})


# %% Level 4
ds_circle_list = [
    l4.swap_dims({"circle": "circle_id"}).sel(circle_id=cs["segment_id"])
    for cs in atr_circle_segments
]
l4_atr = (
    xr.concat(ds_circle_list, dim="circle_id")
    .swap_dims({"circle_id": "circle"})
    .drop_dims("sonde")
)

# Select sondes in East versus West Atlantic
# %% Level 3
l3_west = l3.where(l3.launch_lon <= -40, drop=True)
l3_east = l3.where(l3.launch_lon > -40, drop=True)
sondes_east_no_atr = [
    sid for sid in l3_east.sonde_id.values if sid not in l3_atr.sonde_id.values
]
l3_east_no_atr = (
    l3_east.swap_dims({"sonde": "sonde_id"})
    .sel(sonde_id=sondes_east_no_atr)
    .swap_dims({"sonde_id": "sonde"})
)
# %% Level 4
l4_west = l4.where(l4.circle_lon <= -40, drop=True)
l4_east = l4.where(l4.circle_lon > -40, drop=True)
circles_east_no_atr = [
    cid for cid in l4_east.circle_id.values if cid not in l4_atr.circle_id.values
]
l4_east_no_atr = (
    l4_east.swap_dims({"circle": "circle_id"})
    .sel(circle_id=circles_east_no_atr)
    .swap_dims({"circle_id": "circle"})
)

# %%

variables = ["theta", "rh", "u", "v"]
units = ["K", "%", "m s-1", "m s-1"]

colors = {
    "all": "C0",
    "west": "C2",
    "east": "#c1121f",
    "atr": settings.colors.get("atr", "C2"),
}
labels = {
    "all": "BEACH",
    "west": "< -40˚E",
    "east": "> -40˚E\nwithout ATR",
    "atr": "> -40˚E\nonly ATR",
}

altmax = 11200

# %% Profiles of theta, rh, u, v
cm = 1 / 2.54
sns.set_context("paper", font_scale=0.8)
plt.style.use("./beach.mplstyle")

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14 * cm, 16 * cm), sharey=True)
print(axes.flatten())
for ax, var, unit in zip(axes.flatten(), variables, units):
    for ds, region in zip(
        [l3, l3_west, l3_east_no_atr, l3_atr], ["all", "west", "east", "atr"]
    ):
        ds[var].mean("sonde").sel(altitude=slice(0, altmax)).plot(
            ax=ax, y="altitude", c=colors[region], label=labels[region], zorder=2
        )
    # for sonde in l3_atr.sonde:
    #    l3_atr.sel(sonde=sonde)[var].plot(ax=ax, y="altitude", c=color_atr, alpha=.05, zorder=0)
    for circle in l4_atr.circle:
        l4_atr.sel(circle=circle)[var + "_mean"].plot(
            ax=ax, y="altitude", c=colors["atr"], alpha=0.1, zorder=1
        )
    ax.set_ylabel("altitude / m" if ax == axes[0, 0] or ax == axes[1, 0] else "")
    ax.set_xlabel(f"{var} / {unit}")
    # ax.fill_between([l3[var].min(), l3[var].max()], alt_lim, 15000, color="white", alpha=.7, zorder=10)
    ax.set_ylim(0, 15000)
    ax.set_title("")
axes[0, 0].legend()
axes[1, 0].set_xlim(-20, 10)
axes[1, 1].set_xlim(-10, 15)

fig.savefig("../images/profiles_east_atr_q_theta_u_v.pdf", dpi=300, bbox_inches="tight")

# %% Profiles of divergence and omega


cm = 1 / 2.54
sns.set_context("paper", font_scale=0.8)
plt.style.use("./beach.mplstyle")
fig, axes = plt.subplots(ncols=2, figsize=(12 * cm, 6 * cm), sharey=True)
# for ax, var in zip(axes, ["div", "omega"]):
for ds, region in zip(
    [l4, l4_west, l4_east_no_atr, l4_atr], ["all", "west", "east", "atr"]
):
    ds["div"].mean("circle").sel(altitude=slice(0, altmax)).plot(
        ax=axes[0], y="altitude", c=colors[region], label=labels[region]
    )
    (ds["omega"] * 0.01 * 60 * 60).mean("circle").sel(altitude=slice(0, altmax)).plot(
        ax=axes[1], y="altitude", c=colors[region], label=labels[region]
    )
for circle in l4_atr.circle:
    (l4_atr.sel(circle=circle)["omega"] * 0.01 * 60 * 60).plot(
        ax=axes[1], y="altitude", c=colors["atr"], alpha=0.1, zorder=1
    )
    (l4_atr.sel(circle=circle)["div"]).plot(
        ax=axes[0], y="altitude", c=colors["atr"], alpha=0.1, zorder=1
    )


for ax in axes:
    ax.set_title("")
    ax.axvline(0, color="k", linewidth=0.5, zorder=0)
axes[1].legend(loc="upper right", bbox_to_anchor=(1.03, 1.03))
axes[0].set_xlabel("divergence / s-1")
axes[1].set_xlabel("$\omega$ / hPa hr-1")
axes[0].set_ylabel("altitude / m")
axes[0].set_ylim(0, 15000)
axes[1].set_ylabel("")

fig.savefig("../images/profiles_east_atr_div_omega.pdf", dpi=300, bbox_inches="tight")

# %% Plot the IWV histograms and WS histograms, again for PERCUSION, East, ATR
fig, axes = plt.subplots(1, 2, figsize=(14 * cm, 7 * cm))
for ds, region in zip([l3, l3_east, l3_atr], ["all", "east", "atr"]):
    for ax, var, bins in zip(
        axes, ["iwv", "wspd_sfc"], [np.arange(28, 74, 2), np.arange(0, 30, 1)]
    ):
        ds[var].plot.hist(
            ax=ax,
            bins=bins,
            density=True,
            histtype="step",
            linewidth=3,
            color=colors[region],
            label=labels[region],
        )
        ax.axvline(ds[var].median().values, color=colors[region], linewidth=1)
        ax.set_title("")

ax.legend(loc="upper right")
fig.savefig("../images/hist_east_atr_iwv_ws.pdf", dpi=300, bbox_inches="tight")


# %% Plot PDFs instead of histograms
def density(x, mu, sigma=0.2):
    return 1 / (np.sqrt(2 * np.pi * sigma**2)) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


# %%
fig, ax = plt.subplots(figsize=(12 * cm, 7 * cm))
for ds, region in zip(
    [l3, l3_west, l3_east_no_atr, l3_atr], ["all", "west", "east", "atr"]
):
    density(
        x=xr.DataArray(data=np.arange(0, 80, 1), dims="nodes"),
        mu=ds.iwv,
        sigma=2,
    ).mean("sonde").plot(x="nodes", color=colors[region], label=labels[region])
ax.set_xlim(25, 75)
ax.legend(loc="upper left")
ax.set_ylabel("probability Density")
ax.set_xlabel("integrated water vapor / kg m-2")
ax.set_title("")
fig.savefig("../images/pdf_east_atr_iwv.pdf", dpi=300, bbox_inches="tight")

# %%
fig, ax = plt.subplots(figsize=(12 * cm, 7 * cm))
for ds, region in zip(
    [l3, l3_west, l3_east_no_atr, l3_atr], ["all", "west", "east", "atr"]
):
    density(
        x=xr.DataArray(data=np.arange(0, 40, 1), dims="nodes"),
        mu=ds.wspd_sfc,
        sigma=1,
    ).mean("sonde").plot(x="nodes", color=colors[region], label=labels[region])
ax.set_xlim(0, 35)
ax.legend(loc="upper right")
ax.set_ylabel("Probability Density")
ax.set_xlabel("Near-surface wind speed / m s-1")
ax.set_title("")
fig.savefig("../images/pdf_east_atr_nsfc_ws.png", dpi=300, bbox_inches="tight")
