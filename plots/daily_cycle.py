# %%
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import settings
from xhistogram.xarray import histogram


# %% Load the dropsonde data
l3 = xr.open_dataset(
    f"{settings.root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr",
    engine="zarr",
).assign(wspd_sfc=lambda ds: ds.wspd.sel(altitude=slice(0, 51)).mean("altitude"))


# %%
def solar_local_time(lon, utctime_h):
    return (utctime_h + (lon / 360 * 24)) % 24


l3time = l3.assign(
    utctime=xr.DataArray(
        data=[
            pd.Timestamp(i).hour
            + pd.Timestamp(i).minute / 60
            + pd.Timestamp(i).second / 3600
            for i in l3.launch_time.values
        ],
        dims=["sonde"],
    )
)
l3time = l3time.assign(
    solartime=xr.DataArray(
        data=solar_local_time(l3.launch_lon, l3time.utctime), dims=["sonde"]
    )
)

# %%
plt.style.use("./beach.mplstyle")
colors = {
    "all": "C0",
    "west": "C2",
    "east": "#c1121f",
}
labels = {
    "all": "All PERCUSION",
    "west": "West Atlantic",
    "east": "East Atlantic",
}
# %%
fig, ax = plt.subplots(figsize=(7, 4))
l3time.utctime.plot.hist(bins=np.arange(0, 25, 1), xlim=(10, 24))
ax.set_xlabel("Time (UTC)")
ax.set_ylabel("Counts")

# %%
fig, ax = plt.subplots(figsize=(7, 4))
l3time.solartime.where(l3time.launch_lon > -40, drop=True).plot.hist(
    bins=np.arange(0, 25, 1),
    histtype="step",
    label=labels["east"],
    color=colors["east"],
    lw=5,
)
l3time.solartime.where(l3time.launch_lon < -40, drop=True).plot.hist(
    bins=np.arange(0, 25, 1),
    histtype="step",
    label=labels["west"],
    color=colors["west"],
    lw=5,
)
l3time.solartime.plot.hist(
    bins=np.arange(0, 25, 1),
    histtype="step",
    label=labels["all"],
    color=colors["all"],
)
ax.set_ylabel("Counts")
ax.set_xticks(np.arange(0, 27, 3))
ax.set_xlim(0, 24)
ax.set_xlabel("Local solar time / hour")
fig.legend()
fig.savefig("../images/drop_solartime.png", dpi=300, bbox_inches="tight")

# %% Which launches happened after 7pm?
l3time.where(l3time.solartime > 19, drop=True).launch_time.values

# %% 2d histogram IWV - solar time
fig, ax = plt.subplots(figsize=(7, 4))
hx = histogram(
    l3time.iwv,
    l3time.solartime,
    bins=[np.arange(20, 80, 1), np.arange(0, 25, 1)],
    dim=["sonde"],
)
hx.plot(ax=ax)
ax.axhline(48, c="orange", lw=1)
ax.set_xticks(np.arange(0, 27, 3))
ax.set_xlim(0, 24)
ax.set_xlabel("Local solar time / hour")
fig.savefig("../images/drop_solartime_IWV.png", dpi=300, bbox_inches="tight")

# %% 2d histogram WS_sfc - solar time
fig, ax = plt.subplots(figsize=(7, 4))
hx = histogram(
    l3time.wspd_sfc,
    l3time.solartime,
    bins=[np.arange(0, 20, 1), np.arange(0, 25, 1)],
    dim=["sonde"],
)
hx.plot(ax=ax)
ax.axhline(3, c="orange", lw=1)
ax.set_xticks(np.arange(0, 27, 3))
ax.set_xlim(0, 24)
ax.set_xlabel("Local solar time / hour")
ax.set_ylabel("Near-surface wind speed / m s-1")
fig.savefig("../images/drop_solartime_WSsfc.png", dpi=300, bbox_inches="tight")
