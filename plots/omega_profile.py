# %%
import xarray as xr
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import eurec4a
import settings

# %%
l4_path = f"{settings.root}/products/HALO/dropsondes/Level_4/"
lev4 = xr.open_dataset(os.path.join(l4_path, "PERCUSION_Level_4.zarr"), engine="zarr")
# %%


def assign_island(lon):
    if lon > -40:
        return "SAL"
    else:
        return "BB"


island = lev4.aircraft_longitude.to_series().apply(assign_island)
circle_island = lev4.circle_lon.to_series().apply(assign_island)
ds_island = xr.DataArray(island, dims="sonde", name="island")
c_island = xr.DataArray(circle_island, dims="circle", name="c_island")
ds = lev4.assign_coords(island=ds_island, c_island=c_island)

# %% special ticks


ta_sal = ds.where(ds.aircraft_longitude > -40, drop=True).sel(circle=0).ta.mean("sonde")
ta_bb = (
    ds.where(ds.aircraft_longitude < -40, drop=True).isel(circle=-1).ta.mean("sonde")
)

sal_freeze = np.abs(ta_sal - 273.15).argmin()
bb_freeze = np.abs(ta_bb - 273.15).argmin()

# %% omega vs joanne


cm = 1 / 2.54
cat = eurec4a.get_intake_catalog()
joanne = cat.dropsondes.JOANNE.level4.to_dask()
plt.style.use("./beach.mplstyle")
fig, axes = plt.subplots(ncols=2, figsize=(12 * cm, 6 * cm))

ds.omega.mean("circle").plot(y="altitude", label="BEACH", color="C0", ax=axes[1])

ds.omega.where(ds.omega.c_island == "SAL").mean("circle").plot(
    y="altitude", label="BEACH East Atlantic", color="C2", ax=axes[1]
)
ds.omega.where(ds.omega.c_island == "BB").mean("circle").plot(
    y="altitude", label="BEACH West Atlantic", color="C3", ax=axes[1]
)

(joanne.omega * 60 * 60 / 100).sel(alt=slice(0, 9500)).mean("circle").plot(
    ax=axes[1], y="alt", color="C1", label="JOANNE"
)
ds.div.mean("circle").plot(y="altitude", label="BEACH ", color="C0", ax=axes[0])

ds.div.where(ds.omega.c_island == "SAL").mean("circle").plot(
    y="altitude", label="BEACH East Atlantic", color="C2", ax=axes[0]
)
ds.div.where(ds.omega.c_island == "BB").mean("circle").plot(
    y="altitude", label="BEACH West Atlantic", color="C3", ax=axes[0]
)
joanne.D.mean("circle").plot(ax=axes[0], y="alt", color="C1", label="JOANNE")

axes[1].set_xlabel(f"omega / {ds.omega.attrs['units']}")
axes[0].set_xlabel(f"divergence / {ds.div.attrs['units']}")
axes[1].set_ylabel("")
axes[1].set_yticklabels("")
axes[0].set_ylabel(f"altitude / {ds.altitude.attrs['units']}")
axes[0].legend(loc="center right")
freeze_alt = (sal_freeze + bb_freeze) / 2 * 10
axes[0].set_yticks(
    list(axes[0].get_yticks()) + [freeze_alt],
    labels=list(axes[0].get_yticks()) + ["273.15 K"],
)

for ax in axes:
    ax.set_ylim(0, 13500)
    ax.axvline(0, color="gray", alpha=0.5)
    ax.axhline(freeze_alt, color="gray", alpha=0.5, linestyle=":")

sns.despine(offset={"left": 10})
fig.savefig("../images/joanne_vs_beach.pdf", bbox_inches="tight")
