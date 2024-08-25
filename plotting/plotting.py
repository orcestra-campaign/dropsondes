import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.cm as cm
from datetime import datetime
from goes2go.data import goes_nearesttime
import cartopy.crs as ccrs
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import colors


def individual_sondes_profiles(
    flight_id,
    filepath_list,
    sonde_ds_list,
    loc_list,
    variables,
    units,
    colormap="viridis",
):
    """
    Plot for individual selected sondes. Plotting profiles of variables listed for sondes listed. One should also provide
    a list of locations of the sondes (e.g. "east on north circle" or "north on ATR circle").
    """

    # Create a colormap
    cmap = cm.get_cmap(colormap, len(sonde_ds_list))

    # Create a figure with subplots
    fig, axs = plt.subplots(
        1, len(variables), figsize=(18, 8), sharey=True
    )  # 1 row, 5 columns, adjusted figure size
    fs = 14

    for i, var in enumerate(variables):
        for j, sonde in enumerate(sonde_ds_list):
            file_name = filepath_list[j].split("/")[-1]
            timestamp = file_name.split("_")[2].split(".")[0]
            time_only = timestamp.split("T")[1][:5]

            # Plot on each subplot
            color = cmap(j)
            im_profiles = axs[i].scatter(
                sonde[var],
                sonde.gpsalt,
                c=color,
                s=10,
                label=time_only + f" ({loc_list[j]})",
            )
            axs[i].tick_params(axis="both", which="major", labelsize=fs - 1)
            axs[i].margins(y=0)
            axs[i].spines[["right", "top"]].set_visible(False)

        axs[i].set_xlabel(var + " / " + units[i], fontsize=fs)

    axs[0].set_ylabel("Altitude / m", fontsize=fs)
    axs[2].legend(fontsize=fs - 3)
    plt.suptitle(f"{flight_id} (Level 2)", fontsize=fs + 2)

    return im_profiles


def convert_time_to_str(time=None, time_format="%Y%m%d %H:%M:%S"):
    """
    Convert input time into desired string format.
    """

    # Ensure time is in correct format
    timestamp = (time - np.datetime64("1970-01-01T00:00:00")) / np.timedelta64(1, "s")
    datetime_time = datetime.utcfromtimestamp(timestamp)
    str_time = datetime_time.strftime(time_format)

    return str_time


def get_mean_launch_time(ds_flight=None, time_format="%Y%m%d %H:%M:%S"):
    """
    Compute mean launch time from all sondes in the dataset.
    """

    mean_time = convert_time_to_str(
        ds_flight.interpolated_time[0].mean().values, time_format
    )

    return mean_time


def _create_GOES_variable(goes_object: xr.Dataset, variable: str, gamma: float = 1.2):
    GOES_PRODUCT_DICT = {
        "AirMass": goes_object.rgb.AirMass,
        "AirMassTropical": goes_object.rgb.AirMassTropical,
        "AirMassTropicalPac": goes_object.rgb.AirMassTropicalPac,
        "Ash": goes_object.rgb.Ash,
        "DayCloudConvection": goes_object.rgb.DayCloudConvection,
        "DayCloudPhase": goes_object.rgb.DayCloudPhase,
        "DayConvection": goes_object.rgb.DayConvection,
        "DayLandCloud": goes_object.rgb.DayLandCloud,
        "DayLandCloudFire": goes_object.rgb.DayLandCloudFire,
        "DaySnowFog": goes_object.rgb.DaySnowFog,
        "DifferentialWaterVapor": goes_object.rgb.DifferentialWaterVapor,
        "Dust": goes_object.rgb.Dust,
        "FireTemperature": goes_object.rgb.FireTemperature,
        "NaturalColor": goes_object.rgb.NaturalColor(gamma=gamma),
        "NightFogDifference": goes_object.rgb.NightFogDifference,
        "NighttimeMicrophysics": goes_object.rgb.NighttimeMicrophysics,
        "NormalizedBurnRatio": goes_object.rgb.NormalizedBurnRatio,
        "RocketPlume": goes_object.rgb.RocketPlume,
        "SeaSpray": goes_object.rgb.SeaSpray(gamma=gamma),
        "SplitWindowDifference": goes_object.rgb.SplitWindowDifference,
        "SulfurDioxide": goes_object.rgb.SulfurDioxide,
        "TrueColor": goes_object.rgb.TrueColor(gamma=gamma),
        "WaterVapor": goes_object.rgb.WaterVapor,
    }
    return GOES_PRODUCT_DICT[variable]


def goes_overlay(
    image_date, ax, satellite="16", product="ABI", domain="F", variable="TrueColor"
):
    snapshot = goes_nearesttime(
        image_date, satellite=satellite, product=product, domain=domain
    )
    im_sat = ax.imshow(
        _create_GOES_variable(snapshot, variable),
        transform=snapshot.rgb.crs,
        regrid_shape=3500,
        interpolation="nearest",
    )
    return im_sat


def dropsondes_overlay(
    dropsonde_ds,
    ax,
    variable="iwv",
    variable_label=r"Integrated Water Vapor / kg m$^{-2}$",
    colormap="Blues",
    alpha=1,
    vmin=45,
    vmax=70,
    nlevels=9,
):
    cmap = plt.cm.Blues
    levels = np.linspace(vmin, vmax, nlevels)
    norm = colors.BoundaryNorm(levels, cmap.N)

    im_launches = ax.scatter(
        dropsonde_ds["lon"].isel(alt=10),
        dropsonde_ds["lat"].isel(alt=10),
        marker="o",
        edgecolor="grey",
        s=40,
        transform=ccrs.PlateCarree(),
        c=dropsonde_ds[variable],
        cmap=colormap,
        zorder=10,
        norm=norm,
    )

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="3%", pad=0.4, axes_class=plt.Axes)
    cbar = plt.colorbar(im_launches, cax=cax, orientation="horizontal", ticks=levels)
    cbar.set_label(variable_label)
    cbar.set_ticks(levels)
    cbar.set_label(variable_label)

    return im_launches
