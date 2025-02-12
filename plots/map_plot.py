# %%
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# %%

root = "ipns://latest.orcestra-campaign.org/"
ds = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr", engine="zarr"
)
# %%

ds_sfc = ds.sel(gpsalt=slice(0, 50)).mean("gpsalt").load()
# %%
cmap = "twilight_shifted"
lon_min, lon_max, lat_min, lat_max = -65, -15, -2, 22


fig, ax = plt.subplots(figsize=(12, 6), subplot_kw={"projection": ccrs.PlateCarree()})

ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
p = ax.scatter(ds_sfc.lon.values, ds_sfc.lat.values, c=ds_sfc.w_dir, cmap=cmap)
ax.coastlines(alpha=1.0)
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, alpha=0.25)

# fig.tight_layout()
fig.subplots_adjust(left=0, right=0.9)
cax = fig.add_axes([0.92, 0.09, 0.02, 0.8])
fig.colorbar(p, cax=cax, shrink=0.5)
fig.savefig("../images/w_dir.pdf")
