import settings
import cartopy.crs as ccrs


def get_colors(circle_names):
    mpi_colors = ["#1A237E", "#1976D2", "#81D4FA", "#00695C"]
    atr_colors = ["#FF8F00", "#FFC107"]
    colors = {}
    for circle in circle_names:
        if "atr" in circle:
            colors[circle] = atr_colors.pop(0)
        else:
            colors[circle] = mpi_colors.pop(0)
    return colors


def set_yticks_with_color(axes, yticks, ytick_colors, **kwargs):
    for ax in axes:
        ax.set_yticks(yticks, **kwargs)
        yticks_ax = ax.yaxis.get_major_ticks()
        for tick, c in zip(yticks_ax, ytick_colors):
            tick.tick1line.set_markeredgecolor(c)
            tick.tick2line.set_markeredgecolor(c)


def set_xticks_with_color(axes, xticks, xtick_colors, **kwargs):
    for ax in axes:
        ax.set_xticks(xticks, **kwargs)
        xticks_ax = ax.xaxis.get_major_ticks()
        for tick, c in zip(xticks_ax, xtick_colors):
            tick.tick1line.set_markeredgecolor(c)
            tick.tick2line.set_markeredgecolor(c)


# %%
def plot_gridlines(ax):
    east_region = settings.east_region
    north_region = settings.north_region
    west_region = settings.west_region
    xticks = [
        west_region[0][0],
        west_region[1][0],
        east_region[0][0],
        north_region[0][0],
        east_region[1][0],
    ]
    ax.set_xticks(
        xticks,
        crs=ccrs.PlateCarree(),
    )
    ax.set_xticklabels(xticks, fontsize=6)
    yticks = [
        west_region[0][1],
        west_region[2][1],
        east_region[0][1],
        north_region[2][1],
        east_region[2][1],
    ]
    ax.set_yticks(
        yticks,
        crs=ccrs.PlateCarree(),
    )
    ax.set_yticklabels(yticks, fontsize=6)

    for region, region_name in [
        (east_region, "East"),
        (north_region, "North"),
        (west_region, "West"),
    ]:
        xmin = ax.transLimits.transform(region[0])[0]
        xmax = ax.transLimits.transform(region[1])[0]
        ax.axhline(
            region[0][1],
            xmin=xmin,
            xmax=xmax,
            color="k",
            linewidth=0.5,
            alpha=0.8,
            linestyle="--",
        )
        ax.axhline(
            region[2][1],
            xmin=xmin,
            xmax=xmax,
            color="k",
            linewidth=0.5,
            alpha=0.8,
            linestyle="--",
        )
    ax.text(
        x=east_region[0][0] - 1.5,
        y=(east_region[0][1] - 1.5),
        s="East",
        fontsize=6,
    )
    ax.text(
        x=west_region[0][0] + 2.5,
        y=(west_region[0][1] + 0.7),
        s="West",
        fontsize=6,
    )
    ax.text(
        x=north_region[1][0] - 0.5,
        y=(north_region[3][1] + 0.5),
        s="North",
        fontsize=6,
    )
    return ax
