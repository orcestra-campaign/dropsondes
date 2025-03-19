# %%

import xarray as xr
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import settings

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

rhmax_sal = sal["rh"].mean("sonde").argmax()
rhmax_bb = bb["rh"].mean("sonde").argmax()
rhfreeze_sal = sal["rh"].isel(altitude=sal_freeze).mean("sonde")
rhfreeze_bb = bb["rh"].isel(altitude=sal_freeze).mean("sonde")

# %%


plt.style.use("./beach.mplstyle")
csal = "#960018"
csal_mean = "#c1121f"
cbb = "#0085db"
cbb_mean = "#00b4d8"
variables = ["theta", "rh", "u", "v"]
units = ["K", "%", "m s-1", "m s-1"]


fig, axes = plt.subplots(ncols=4, figsize=(24, 6), sharey=True)

for j, var in enumerate(variables):
    col = j % 2
    row = j // 2
    ax = axes[j]  # axes[row, col]
    for i in range(max([sal.sonde.size, bb.sonde.size])):
        sonde = max([sal.sonde.size, bb.sonde.size]) - i - 1

        try:
            sal.sel(sonde=sonde)[var].plot(ax=ax, color=csal, alpha=0.05, y="altitude")
        except IndexError:
            pass
        bb.sel(sonde=sonde)[var].plot(ax=ax, color=cbb, alpha=0.05, y="altitude")

    sal[var].mean("sonde").sel(altitude=slice(0, 13500)).plot(
        ax=ax, color=csal_mean, y="altitude", linewidth=5, label="East Atlantic"
    )
    bb[var].mean("sonde").sel(altitude=slice(0, 13500)).plot(
        ax=ax, color=cbb_mean, y="altitude", linewidth=5, label="West Atlantic"
    )
    ax.set_xlabel(f"{var} / {units[j]}")

sns.despine(offset=10)
axes[0].set_yticks(
    list(axes[0].get_yticks())
    + [(sal_freeze + bb_freeze) / 2 * 10, (rhmax_sal + rhmax_bb) / 2 * 10],
    labels=list(axes[0].get_yticks())
    + ["273.15 K", (rhmax_sal + rhmax_bb).values / 2 * 10],
)
xticks = list((axes[1].get_xticks()).astype(int))
xticks.remove(np.float64(60))
axes[1].set_xticks(xticks + [int(rhfreeze_sal), int(rhfreeze_bb)])
axes[0].set_yticks(
    axes[0].get_yticks(), labels=[int(label) for label in axes[0].get_yticks()]
)

for ax in axes.flatten():
    ax.set_ylim(0, 15000)
    ax.set_ylabel("")
for ax in axes[:2]:
    ax.axhline(
        (sal_freeze + bb_freeze) / 2 * 10, color="grey", alpha=0.5, linestyle="--"
    )
axes[1].axhline(
    (rhmax_sal + rhmax_bb) / 2 * 10, color="grey", alpha=0.5, linestyle="--"
)

axes[1].axvline(rhfreeze_sal, color="grey", alpha=0.5, linestyle="--")
axes[1].axvline(rhfreeze_bb, color="grey", alpha=0.5, linestyle="--")
axes[1].set_xlim(0, 100)

axes[3].axhline(
    (rhmax_sal + rhmax_bb) / 2 * 10, color="grey", alpha=0.5, linestyle="--"
)
# for ax in axes[0]:
axes[0].set_ylabel("altitude / m")
sns.despine(offset={"left": 10})
axes[0].legend()
fig.tight_layout()
fig.savefig("../images/profile_overview.png")
