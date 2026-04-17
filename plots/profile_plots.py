# %%

import xarray as xr
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import settings
from orcestra import get_flight_segments
import droputils.data_utils as du

lev3 = xr.open_dataset(
    f"ipfs://{settings.lev3}",
    engine="zarr",
)
# %%
east = du.sel_sub_domain(
    lev3,
    settings.east_region,
    item_var="sonde",
    lon_var="launch_lon",
    lat_var="launch_lat",
)

west = du.sel_sub_domain(
    lev3,
    settings.west_region,
    item_var="sonde",
    lon_var="launch_lon",
    lat_var="launch_lat",
)
north = du.sel_sub_domain(
    lev3,
    settings.north_region,
    item_var="sonde",
    lon_var="launch_lon",
    lat_var="launch_lat",
)
# %%

sal = lev3.where(lev3.launch_lon > -40, drop=True)
bb = lev3.where(lev3.launch_lon < -40, drop=True)
# %%

east = east.assign(rh=east.rh * 100)
west = west.assign(rh=west.rh * 100)
north = north.assign(rh=north.rh * 100)
sal = sal.assign(rh=sal.rh * 100)
bb = bb.assign(rh=bb.rh * 100)
# %%

# %% special ticks


ta_east = east["ta"].mean("sonde")
ta_west = west["ta"].mean("sonde")
ta_north = north["ta"].mean("sonde")

east_freeze = np.abs(ta_east - 273.15).argmin()
west_freeze = np.abs(ta_west - 273.15).argmin()
north_freeze = np.abs(ta_north - 273.15).argmin()
rhfreeze_east = east["rh"].isel(altitude=east_freeze).mean("sonde")
rhfreeze_west = west["rh"].isel(altitude=west_freeze).mean("sonde")
rhfreeze_north = north["rh"].isel(altitude=north_freeze).mean("sonde")
# %%

meta = get_flight_segments()
entries = []
atr = []
for key in meta["HALO"].keys():
    for entry in meta["HALO"][key]["segments"]:
        if ("atr_coordination" in entry["kinds"]) and ("circle" in entry["kinds"]):
            print(entry["segment_id"], entry["start"], entry["end"])
            segment_sondes = (
                lev3.swap_dims({"sonde": "launch_time"})
                .sel(launch_time=slice(entry["start"], entry["end"]))
                .swap_dims({"launch_time": "sonde"})
            )
            try:
                extra = (
                    lev3.swap_dims({"sonde": "sonde_id"})
                    .sel(sonde=entry["extra_sondes"])
                    .swap_dims({"sonde_id": "sonde"})
                )
            except KeyError:
                atr.append(segment_sondes)
            else:
                atr.append(xr.concat([segment_sondes, extra], dim="sonde"))
            entries.append(entry)
            print(entry["kinds"])

atr_sondes = xr.concat(atr, dim="sonde")
atr_sondes["rh"] = atr_sondes["rh"] * 100
# %%

sns.set_context("paper", font_scale=0.8)
plt.style.use("./beach.mplstyle")
csal = settings.colors["csal"]
csal_mean = settings.colors["csal_mean"]
atr_color = settings.colors["atr_mean"]
cbb = settings.colors["cbb"]
cbb_mean = settings.colors["cbb_mean"]
variables = ["theta", "rh", "u", "v"]
units = ["K", "%", "m s-1", "m s-1"]


cm = 1 / 2.54
fig, axes = plt.subplots(ncols=2, nrows=2, figsize=(12 * cm, 12 * cm), sharey=True)

for j, var in enumerate(variables):
    col = j % 2
    row = j // 2
    ax = axes[row, col]

    for i in range(max([sal.sonde.size, bb.sonde.size])):
        sonde = max([sal.sonde.size, bb.sonde.size]) - i - 1

        try:
            sal.sel(sonde=sonde)[var].plot(
                ax=ax, color=csal, alpha=0.05, y="altitude", rasterized=True
            )
        except IndexError:
            pass
        bb.sel(sonde=sonde)[var].plot(
            ax=ax, color=cbb, alpha=0.05, y="altitude", rasterized=True
        )

    north[var].mean("sonde").sel(altitude=slice(0, 10000)).plot(
        ax=ax, color=atr_color, y="altitude", linewidth=2, label="North"
    )
    east[var].mean("sonde").sel(altitude=slice(0, 13500)).plot(
        ax=ax, color=csal_mean, y="altitude", linewidth=2, label="East"
    )

    west[var].mean("sonde").sel(altitude=slice(0, 13500)).plot(
        ax=ax, color=cbb_mean, y="altitude", linewidth=2, label="West"
    )
    ax.set_xlabel(f"{var} / {units[j]}")

sns.despine(offset=10)
axes[0, 1].set_yticks(
    list(axes[0, 1].get_yticks()) + [(east_freeze + west_freeze) / 2 * 10],
    labels=list(axes[0, 0].get_yticks()) + ["273.15 K"],
)
xticks = list((axes[0, 1].get_xticks()).astype(int))
xticks.remove(np.float64(60))
axes[0, 1].set_xticks(xticks + [int(rhfreeze_east), int(rhfreeze_west)])
yticks = axes[0, 0].get_yticks()
yticks_new = np.concatenate(
    (yticks, [east_freeze * 10, west_freeze * 10, north_freeze * 10])
)

axes[0, 0].set_yticks(
    np.concatenate((yticks, [east_freeze * 10, west_freeze * 10, north_freeze * 10])),
    labels=yticks.tolist() + ["", "", ""],
)

for ax in axes.flatten():
    ax.set_ylim(0, 15000)
    ax.set_ylabel("")
for ax in axes[0, :]:
    ax.axhline(
        (east_freeze + west_freeze) / 2 * 10, color="grey", alpha=0.5, linestyle="--"
    )


axes[0, 1].axvline(rhfreeze_east, color="grey", alpha=0.5, linestyle="--")
axes[0, 1].axvline(rhfreeze_west, color="grey", alpha=0.5, linestyle="--")
axes[0, 1].set_xlim(0, 100)
axes[0, 0].set_ylabel("altitude / m")
axes[1, 0].set_ylabel("altitude / m")
axes[1, 1].set_xlim(-20, 20)
axes[1, 0].set_xlim(-40, 20)
sns.despine(offset={"left": 5})
axes[0, 0].legend(fontsize=8)
fig.tight_layout()
fig.savefig("../images/profile_overview.pdf", bbox_inches="tight")
