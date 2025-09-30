# %%
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
import numpy as np
import settings
import seaborn as sns
import droputils.plot_utils as pu


# %%

ds = xr.open_dataset(
    f"{settings.root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr",
    engine="zarr",
)


# %%

ds_sfc = ds.sel(altitude=slice(0, 50)).mean("altitude")

sns.set_context("paper", font_scale=0.8)
plt.style.use("./beach.mplstyle")

lon_min, lon_max, lat_min, lat_max = -65, -15, 0, 23

cmap = "twilight_shifted"

size = 2
cm = 1 / 2.54
fig, ax = plt.subplots(
    figsize=(12 * cm, 5.5), subplot_kw=dict(projection=ccrs.PlateCarree())
)

ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor="black", facecolor="lightgrey")
ax = pu.plot_gridlines(ax)

ax.set_title("Surface wind direction")

p = ax.scatter(
    ds_sfc.lon.values,
    ds_sfc.lat.values,
    c=ds_sfc.wdir,
    cmap=cmap,
    s=size,
)

ax1 = fig.add_axes((0.89, 0.36, 0.06, 0.06), projection="polar")

azimuths = np.arange(0, 361, 1)
zeniths = np.arange(40, 70, 1)
values = azimuths * np.ones((30, 361))
ax1.pcolormesh(azimuths * np.pi / 180.0, zeniths, values, cmap=cmap)
ax1.set_yticklabels("")
ax1.set_theta_zero_location("N")
ax1.set_theta_direction(-1)
ax1.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
ax1.set_xticklabels(["N", "", "E", "", "S", "", "W", ""])
ax1.tick_params(axis="x", which="major", pad=-7, labelsize=6)
ax1.grid(False)
ax.set_xlabel("Longitude / °E")
ax.set_ylabel("Latitude / °N")
fig.tight_layout()
fig.savefig("../images/map_wdir.pdf", bbox_inches="tight")


# %% iwv
ds_iwv = ds.iwv

lon_min, lon_max, lat_min, lat_max = -65, -15, 0, 23
cmap = "BrBG"

fig, ax = plt.subplots(
    figsize=(12 * cm, 5.5), subplot_kw=dict(projection=ccrs.PlateCarree())
)

ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor="black", facecolor="lightgrey")
ax = pu.plot_gridlines(ax)

ax.set_title("Integrated water vapor")

p = ax.scatter(
    ds_iwv.launch_lon.values,
    ds_iwv.launch_lat.values,
    c=ds_iwv,
    cmap=cmap,
    s=size,
    vmin=25,
    vmax=71,
)

cax = fig.add_axes((0.91, 0.34, 0.01, 0.15))
cb = fig.colorbar(p, cax=cax, ticks=[30, 48, 55, 70], extend="max")
cb.set_ticklabels(["30", "48", "55", "70"], fontsize=5.5)
ax.set_xlabel("Longitude / °E")
ax.set_ylabel("Latitude / °N")
fig.tight_layout()
fig.savefig("../images/map_iwv.pdf", bbox_inches="tight")
