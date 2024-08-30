import numpy as np
import xarray as xr
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import colors
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


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
    from goes2go.data import goes_nearesttime

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


def individual_sondes_profiles(
    flight_id,
    filepath_list,
    sonde_ds_list,
    loc_list,
    variables,
    units,
    colormap="viridis",
    fs=14,
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


def launch_locations_map(ds_flight, flight_id, fs=14):
    print("Plotting launch locations with IWV...")

    fig = plt.figure(figsize=(12, 8))

    ax = plt.axes(projection=ccrs.AzimuthalEquidistant())
    ax.coastlines(resolution="50m", linewidth=1.5)

    # Plot the flight path
    ax.plot(
        ds_flight["lon"].isel(alt=-700),
        ds_flight["lat"].isel(alt=-700),
        c="grey",
        linestyle=":",
        transform=ccrs.PlateCarree(),
    )

    # Scatter plot for launch locations
    im = ax.scatter(
        ds_flight["lon"].isel(alt=-700),
        ds_flight["lat"].isel(alt=-700),
        marker="o",
        edgecolor="grey",
        s=60,
        transform=ccrs.PlateCarree(),
        c=ds_flight["iwv"],
        cmap="Blues_r",
        vmin=45,
        vmax=70,
    )

    # Set plot boundaries
    lon_w = -35
    lon_e = -13
    lat_s = 1
    lat_n = 22
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
        alpha=0.6,
        linestyle="--",
    )
    gl.xlocator = mticker.FixedLocator(xticks)
    gl.ylocator = mticker.FixedLocator(yticks)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {"size": fs, "color": "k"}
    gl.ylabel_style = {"size": fs, "color": "k"}

    # Colorbar adjustments
    cax = fig.add_axes([0.25, 0.001, 0.5, 0.02])
    cbar = fig.colorbar(im, cax=cax, orientation="horizontal")
    cbar.set_label("Integrated Water Vapour (kg m$^{-2}$)", fontsize=fs)
    cbar.ax.tick_params(labelsize=fs - 2)

    # Save the figure
    plt.savefig(
        f"../../figures/HALO-{flight_id}a/HALO_Dropsondes-launch_locations_iwv-{flight_id}.png",
        bbox_inches="tight",
    )


def lat_time_plot(ds_flight, flight_id, fs=14):
    print("Plotting spatio-temporal variation (lat v/s time) with IWV...")

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(15, 5))

    # Plotting
    scatter = ax.scatter(
        ds_flight["launch_time"].values,
        ds_flight["lat"].isel(alt=-700).values,
        s=90,
        c=ds_flight["iwv"].values,
        edgecolor="grey",
        cmap="Blues_r",
        vmin=45,
        vmax=70,
    )

    # Set x-axis limits
    ax.set_xlim(
        np.min(ds_flight["launch_time"].values) - np.timedelta64(4, "m"),
        np.max(ds_flight["launch_time"].values) + np.timedelta64(4, "m"),
    )

    # Hide the top and right spines
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("IWV / kg m$^{-2}$", fontsize=fs - 2)

    # Format the x-axis with time
    myFmt = mdates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(myFmt)

    # Set labels
    ax.set_xlabel("Time / UTC", fontsize=fs)
    ax.set_ylabel("Latitude / $\degree$N", fontsize=fs)

    # Save the figure
    plt.savefig(
        f"../../figures/HALO-{flight_id}a/HALO_Dropsondes-spatiotemporal_variation_iwv-{flight_id}.png",
        bbox_inches="tight",
    )


def all_profiles(ds_flight, flight_id, fs=14):
    row = 1
    col = 5

    fig, ax = plt.subplots(row, col, sharey=True, figsize=(14, 6))

    r = ["tdry", "theta", "theta_v", "rh", "wspd", "wdir"]
    r_titles = [
        "T / $\degree$C",
        "$\\theta$ / K",
        "$\\theta_v$ / K",
        "RH / %",
        "Wind speed / ms$^{-1}$",
        "Wind direction / $\degree$",
    ]

    print(f"Plotting vertical profiles of {r}...")

    for j in range(col):
        d = ds_flight[r[j]]
        for i in range(1, len(ds_flight["launch_time"]) - 1):
            ax[j].plot(
                d.isel(launch_time=i),
                ds_flight["alt"] / 1000,
                c="grey",
                alpha=0.25,
                linewidth=0.5,
            )

        ax[j].plot(
            np.nanmean(d, axis=0),
            ds_flight["alt"] / 1000,
            linewidth=3,
            c="k",
        )
        ax[j].set_xlabel(r_titles[j], fontsize=fs)
        ax[j].spines["right"].set_visible(False)
        ax[j].spines["top"].set_visible(False)
        if j == 0:
            ax[j].set_ylabel("Altitude (km)", fontsize=fs)

    plt.savefig(
        f"../../figures/HALO-{flight_id}a/HALO_Dropsondes-vertical_profiles_measured_quantities-{flight_id}.png",
        bbox_inches="tight",
    )


def drift_plots(ds_flight, flight_id, fs=14):
    print("Plotting drift in lat and lon...")

    f, ax = plt.subplots(1, 2, sharey=True, figsize=(10, 5))

    for i in range(len(ds_flight["launch_time"])):
        max_id = np.max(np.where(~np.isnan(ds_flight["lon"].isel(launch_time=i))))

        ax[0].plot(
            ds_flight["lat"].isel(launch_time=i)
            - ds_flight["lat"].isel(launch_time=i).isel(alt=max_id),
            ds_flight["alt"],
            linewidth=1.5,
            c="grey",
            alpha=0.75,
        )
        # ax[0].plot(
        #     np.mean(ds_flight["lat"] - ds_flight["lat"].isel(alt=max_id), axis=1),
        #     ds_flight["alt"],
        #     linewidth=2,
        #     c="k",
        #     alpha=1,
        # )
        ax[0].set_xlabel("Drift in Latitude ($\degree$)", fontsize=fs)
        ax[0].set_ylabel("Altitude", fontsize=fs)
        ax[0].spines["right"].set_visible(False)
        ax[0].spines["top"].set_visible(False)

        ax[1].plot(
            ds_flight["lon"].isel(launch_time=i)
            - ds_flight["lon"].isel(launch_time=i).isel(alt=max_id),
            ds_flight["alt"],
            linewidth=1.5,
            c="grey",
            alpha=0.75,
        )
        # ax[1].plot(
        #     np.mean(ds_flight["lon"] - ds_flight["lon"].isel(alt=max_id), axis=1),
        #     ds_flight["alt"],
        #     linewidth=2,
        #     c="k",
        #     alpha=1,
        # )
        ax[1].set_xlabel("Drift in Longitude ($\degree$)", fontsize=fs)
        #     ax[1].set_ylabel('Altitude')
        ax[1].spines["right"].set_visible(False)
        ax[1].spines["top"].set_visible(False)
        ax[1].spines["left"].set_visible(False)

    plt.savefig(
        f"../../figures/HALO-{flight_id}a/HALO_Dropsondes-drift_in_lat_lon-{flight_id}.png",
        bbox_inches="tight",
    )


def all_quicklook_plots(ds_flight, flight_id):
    launch_locations_map(ds_flight, flight_id)
    lat_time_plot(ds_flight, flight_id)
    all_profiles(ds_flight, flight_id)
    drift_plots(ds_flight, flight_id)
