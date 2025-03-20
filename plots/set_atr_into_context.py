# %%
import xarray as xr
import matplotlib.pyplot as plt
import settings

from orcestra import get_flight_segments

# %%
# Load the flight segments
meta = get_flight_segments()["HALO"]
segments = [
    {
        **s,
        "flight_id": flight_id,
    }
    for flight_id, flight in meta.items()
    for s in flight["segments"]
]

atr_circle_segments = [
    s for s in segments if "atr_coordination" in s["kinds"] and "circle" in s["kinds"]
]

# %% Load the dropsonde data
l3 = xr.open_dataset(
    f"{settings.root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr",
    engine="zarr",
)
l4 = xr.open_dataset(
    f"{settings.root}/products/HALO/dropsondes/Level_4/PERCUSION_Level_4.zarr",
    engine="zarr",
)
l4
# %% Select only sondes in the East Atlantic
l3_east = l3.where(l3.aircraft_longitude > -40, drop=True)
l4_east = l4.where(l4.circle_lon > -40, drop=True)

# %% Select the sondes in L3 related to ATR coordination
atr_times = [
    slice(s["start"], s["end"]) for s in segments if "atr_coordination" in s["kinds"]
]
ds_atr_list = [
    l3.swap_dims({"sonde": "sonde_time"}).sel(sonde_time=t) for t in atr_times
]
l3_atr = xr.concat(ds_atr_list, dim="sonde_time").swap_dims({"sonde_time": "sonde"})


# %%
ds_circle_list = [
    l4.swap_dims({"circle": "circle_id"}).sel(circle_id=cs["segment_id"])
    for cs in atr_circle_segments
]
l4_atr = (
    xr.concat(ds_circle_list, dim="circle_id")
    .swap_dims({"circle_id": "circle"})
    .drop_dims("sonde")
)

# %%
plt.style.use("./beach.mplstyle")

variables = ["theta", "rh", "u", "v"]
units = ["K", "%", "m s-1", "m s-1"]

color_all = "C0"
color_east = "#c1121f"
color_atr = settings.colors.get("atr", "C2")
altmax = 11200

# %%
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 16), sharey=True)
print(axes.flatten())
for ax, var, unit in zip(axes.flatten(), variables, units):
    l3[var].mean("sonde").sel(altitude=slice(0, altmax)).plot(
        ax=ax, y="altitude", c=color_all, label="All PERCUSION", zorder=2
    )
    l3_east[var].mean("sonde").sel(altitude=slice(0, altmax)).plot(
        ax=ax, y="altitude", c=color_east, label="East Atlantic", zorder=3
    )
    l3_atr[var].mean("sonde").sel(altitude=slice(0, altmax)).plot(
        ax=ax, y="altitude", c=color_atr, label="ATR coordination", zorder=4
    )
    # for sonde in l3_atr.sonde:
    #    l3_atr.sel(sonde=sonde)[var].plot(ax=ax, y="altitude", c=color_atr, alpha=.05, zorder=0)
    for circle in l4_atr.circle:
        l4_atr.sel(circle=circle)[var + "_mean"].plot(
            ax=ax, y="altitude", c=color_atr, alpha=0.1, zorder=1
        )
    ax.set_ylabel("Altitude / m" if ax == axes[0, 0] or ax == axes[1, 0] else "")
    ax.set_xlabel(f"{var} [{unit}]")
    # ax.fill_between([l3[var].min(), l3[var].max()], alt_lim, 15000, color="white", alpha=.7, zorder=10)
    ax.set_ylim(0, 15000)
    ax.set_title("")
axes[0, 0].legend()
axes[1, 0].set_xlim(-20, 10)
axes[1, 1].set_xlim(-10, 15)

fig.savefig("../images/profiles_east_atr_q_theta_u_v.png", dpi=300, bbox_inches="tight")

# %%
fig, axes = plt.subplots(ncols=2, figsize=(14, 7), sharey=True)
for ax, var in zip(axes, ["div", "omega"]):
    l4[var].mean("circle").sel(altitude=slice(0, altmax)).plot(
        ax=ax, y="altitude", c=color_all, label="All PERCUSION", zorder=2
    )
    l4_east[var].mean("circle").sel(altitude=slice(0, altmax)).plot(
        ax=ax, y="altitude", c=color_east, label="East Atlantic", zorder=3
    )
    for circle in l4_atr.circle:
        l4_atr.sel(circle=circle)[var].plot(
            ax=ax, y="altitude", c=color_atr, alpha=0.1, zorder=1
        )
    l4_atr[var].mean("circle").sel(altitude=slice(0, altmax)).plot(
        ax=ax, y="altitude", c=color_atr, label="ATR coordination", zorder=4
    )
    ax.set_ylabel("Altitude / m" if ax == axes[0] else "")
    ax.set_ylim(0, 15000)
    ax.axvline(0, color="k", linewidth=0.5, zorder=0)
axes[1].legend(loc="upper right", bbox_to_anchor=(1.03, 1.03))
axes[0].set_xlabel("Divergence / s-1")
axes[1].set_xlabel("Vertical velocity / Pa s-1")

fig.savefig("../images/profiles_east_atr_div_omega.png", dpi=300, bbox_inches="tight")
