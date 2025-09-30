# %%
import xarray as xr
import os
import matplotlib.pyplot as plt
import seaborn as sns
import eurec4a
import settings
import droputils.data_utils as du

# %%
l4_path = f"{settings.root}/products/HALO/dropsondes/Level_4/"
lev4 = xr.open_dataset(os.path.join(l4_path, "PERCUSION_Level_4.zarr"), engine="zarr")
# %%


def assign_island(lon):
    if lon > -40:
        return "SAL"
    else:
        return "BB"


east = du.sel_sub_domain(
    lev4,
    settings.east_region,
    item_var="circle",
    lon_var="circle_lon",
    lat_var="circle_lat",
)
west = du.sel_sub_domain(
    lev4,
    settings.west_region,
    item_var="circle",
    lon_var="circle_lon",
    lat_var="circle_lat",
)
north = du.sel_sub_domain(
    lev4,
    settings.north_region,
    item_var="circle",
    lon_var="circle_lon",
    lat_var="circle_lat",
)


# %% omega vs joanne

csal = settings.colors["csal_mean"]
cbb = settings.colors["cbb_mean"]
cnorth = settings.colors["atr_mean"]

cm = 1 / 2.54
cat = eurec4a.get_intake_catalog()
joanne = cat.dropsondes.JOANNE.level4.to_dask()
plt.style.use("./beach.mplstyle")
fig, axes = plt.subplots(ncols=2, figsize=(12 * cm, 6 * cm))

(lev4.omega.mean("circle") * 0.01 * 60 * 60).plot(
    y="altitude", label="BEACH", color="k", ax=axes[1]
)

(east.omega.mean("circle") * 0.01 * 60 * 60).plot(
    y="altitude", label="BEACH East", color=csal, ax=axes[1]
)
(west.omega.mean("circle") * 0.01 * 60 * 60).plot(
    y="altitude", label="BEACH West", color=cbb, ax=axes[1]
)
(north.omega.mean("circle") * 0.01 * 60 * 60).sel(altitude=slice(0, 10000)).plot(
    y="altitude", label="BEACH North", color=cnorth, ax=axes[1]
)

(joanne.omega * 60 * 60 / 100).sel(alt=slice(0, 9500)).mean("circle").plot(
    ax=axes[1], y="alt", color="C1", label="JOANNE"
)

lev4.div.mean("circle").plot(y="altitude", label="BEACH", color="k", ax=axes[0])
east.div.mean("circle").plot(y="altitude", label="BEACH East", color=csal, ax=axes[0])
west.div.mean("circle").plot(y="altitude", label="BEACH West", color=cbb, ax=axes[0])
north.div.mean("circle").sel(altitude=slice(0, 10000)).plot(
    y="altitude", label="BEACH North", color=cnorth, ax=axes[0]
)
joanne.D.mean("circle").plot(ax=axes[0], y="alt", color="C1", label="JOANNE")

axes[1].set_xlabel("omega / hPa hr-1")
axes[0].set_xlabel(f"divergence / {lev4.div.attrs['units']}")
axes[1].set_ylabel("")
axes[1].set_yticklabels("")
axes[0].set_ylabel(f"altitude / {lev4.altitude.attrs['units']}")
axes[0].legend(loc="center right")
axes[0].set_yticks(
    list(axes[0].get_yticks()),
    labels=list(axes[0].get_yticks()),
)

for ax in axes:
    ax.set_ylim(0, 13500)
    ax.axvline(0, color="gray", alpha=0.5)

sns.despine(offset={"left": 5})
fig.savefig("../images/joanne_vs_beach.pdf", bbox_inches="tight")
# %%

fig, ax = plt.subplots()

ax.scatter(lev4.circle_lon, lev4.circle_lat, color="red")
ax.scatter(east.circle_lon, east.circle_lat, color="red")
