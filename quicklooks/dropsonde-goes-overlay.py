import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from datetime import datetime
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

from quickgrid import grid_together, derived_products
from quicklooks import goes_overlay, dropsondes_overlay


# -------------------------------------------
################ PLOT FLIGHT ################

flight_time = datetime(2024, 8, 11, 12, 0, 0)
sat_time_str = flight_time.strftime("%Y-%m-%d %H:%M")
flight_time_str = flight_time.strftime("%Y-%m-%d")
flight_name = f"HALO-{flight_time.strftime('%Y%m%d')}a"

flight_date = flight_name[5:9] + "-" + flight_name[9:11] + "-" + flight_name[11:13]

try:
    tracks = xr.open_dataset(
        "/Volumes/ORCESTRA/"
        + flight_name
        + "/bahamas/QL_"
        + flight_name
        + "_BAHAMAS_V01.nc"
    )
    path = LatLon(lat=tracks["IRS_LAT"], lon=tracks["IRS_LON"], label=flight_name)

    fig, ax = plt.subplots(
        figsize=(15, 8),
        facecolor="white",
        subplot_kw={"projection": ccrs.PlateCarree()},
    )

    path_preview(path, ax=ax, show_waypoints=False, color="#FF5349")

except FileNotFoundError:
    fig, ax = plt.subplots(
        figsize=(15, 8),
        facecolor="white",
        subplot_kw={"projection": ccrs.PlateCarree()},
    )

    # Set plot boundaries
    lon_w = -34
    lon_e = -14
    lat_s = 3
    lat_n = 19
    ax.set_extent([lon_w, lon_e, lat_s, lat_n], crs=ccrs.PlateCarree())

    # Assigning axes ticks
    xticks = np.arange(-180, 180, 4)
    yticks = np.arange(-90, 90, 4)

    # Setting up the gridlines
    gl = ax.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=True,
        linewidth=1,
        color="gray",
        alpha=0.5,
        linestyle="-",
    )
    gl.xlocator = mticker.FixedLocator(xticks)
    gl.ylocator = mticker.FixedLocator(yticks)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {"size": 12, "color": "k"}
    gl.ylabel_style = {"size": 12, "color": "k"}


# -------------------------------------------
################ PLOT GOES-16 ################

goes_overlay(sat_time_str, ax)


# -------------------------------------------
################ PLOT DROPSONDES #############

path_to_dropsondes = f"/Volumes/ORCESTRA/{flight_name}/dropsondes"
print(glob.glob("path_to_dropsondes/*"))

# Regrid

dropsonde_ds = grid_together(path_to_dropsondes)
dropsonde_ds = derived_products(dropsonde_ds)

# Plot

dropsondes_overlay(dropsonde_ds, ax)

# Save
plt.savefig(
    f"IWV_QL_dropsondes_PERCUSION_HALO_{flight_time.strftime("%Y%m%d")}.png",
    bbox_inches="tight",
)
