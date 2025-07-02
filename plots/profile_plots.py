# %%

import xarray as xr
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import settings
from orcestra import get_flight_segments

lev3 = xr.open_dataset(
    f"{settings.root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr",
    engine="zarr",
)
# %%

sal = lev3.where(lev3.aircraft_longitude > -40, drop=True)
sal["rh"] = sal["rh"] * 100
bb = lev3.where(lev3.aircraft_longitude < -40, drop=True)
bb["rh"] = bb["rh"] * 100

# %% special ticks


ta_sal = sal["ta"].mean("sonde")
ta_bb = bb["ta"].mean("sonde")

sal_freeze = np.abs(ta_sal - 273.15).argmin()
bb_freeze = np.abs(ta_bb - 273.15).argmin()
rhfreeze_sal = sal["rh"].isel(altitude=sal_freeze).mean("sonde")
rhfreeze_bb = bb["rh"].isel(altitude=sal_freeze).mean("sonde")
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

    sal[var].mean("sonde").sel(altitude=slice(0, 13500)).plot(
        ax=ax, color=csal_mean, y="altitude", linewidth=2, label="East Atlantic"
    )
    bb[var].mean("sonde").sel(altitude=slice(0, 13500)).plot(
        ax=ax, color=cbb_mean, y="altitude", linewidth=2, label="West Atlantic"
    )
    ax.set_xlabel(f"{var} / {units[j]}")

sns.despine(offset=10)
axes[0, 1].set_yticks(
    list(axes[0, 1].get_yticks()) + [(sal_freeze + bb_freeze) / 2 * 10],
    labels=list(axes[0, 0].get_yticks()) + ["273.15 K"],
)
xticks = list((axes[0, 1].get_xticks()).astype(int))
xticks.remove(np.float64(60))
axes[0, 1].set_xticks(xticks + [int(rhfreeze_sal), int(rhfreeze_bb)])


axes[0, 0].set_yticks(
    axes[0, 0].get_yticks(), labels=[int(label) for label in axes[0, 0].get_yticks()]
)

for ax in axes.flatten():
    ax.set_ylim(0, 15000)
    ax.set_ylabel("")
for ax in axes[0, :]:
    ax.axhline(
        (sal_freeze + bb_freeze) / 2 * 10, color="grey", alpha=0.5, linestyle="--"
    )

axes[0, 1].axhline(
    (rhmax_sal + rhmax_bb) / 2 * 10, color="grey", alpha=0.5, linestyle="--"
)

axes[0, 1].axvline(rhfreeze_sal, color="grey", alpha=0.5, linestyle="--")
axes[0, 1].axvline(rhfreeze_bb, color="grey", alpha=0.5, linestyle="--")
axes[0, 1].set_xlim(0, 100)
for ax in axes[1, :]:
    ax.axhline((rhmax_sal + rhmax_bb) / 2 * 10, color="grey", alpha=0.5, linestyle="--")
axes[0, 0].set_ylabel("altitude / m")
axes[1, 0].set_ylabel("altitude / m")
axes[1, 1].set_xlim(-20, 20)
axes[1, 0].set_xlim(-40, 20)
sns.despine(offset={"left": 10})
axes[0, 0].legend()
fig.tight_layout()
fig.savefig("../images/profile_overview.pdf", bbox_inches="tight")
