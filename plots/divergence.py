# %%
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import settings
import eurec4a

# %%
l4_path = f"{settings.root}/products/HALO/dropsondes/Level_4/PERCUSION_Level_4.zarr"
ds_lev4 = xr.open_dataset(l4_path, engine="zarr").load()


def get_nb_circles_per_flight(ds):
    fids = np.unique(ds.flight_id)
    flights = {}
    for fid in fids:
        flights[fid] = ds.where(ds.flight_id == fid, drop=True).sizes["circle"]

    return flights


circle_flights = get_nb_circles_per_flight(ds_lev4)
# %%
cm = 1 / 2.54
plt.style.use("./beach.mplstyle")
fig, ax = plt.subplots(figsize=(12 * cm, 4 * cm))
im = (ds_lev4.div).plot(
    cmap="coolwarm",
    ax=ax,
    y="altitude",
    center=0,
    vmin=-3e-5,
    vmax=3e-5,
    rasterized=True,
    add_colorbar=False,
)
fig.subplots_adjust(right=0.93)
cax = fig.add_axes([0.95, 0.15, 0.01, 0.7])
fig.colorbar(im, cax=cax, label="divergence / s-1", extend="both")
nb_circ = 0
xpos = np.insert(np.cumsum(list(circle_flights.values())) - 0.5, 0, -0.5)

xtickpos = [(xpos[i] + xpos[i + 1]) / 2 for i in range(len(xpos) - 1)]
xlabels = (
    [
        "\n" * (i % 2) + f"{flight}".split("-")[1].split("a")[0]
        for i, flight in enumerate(list(circle_flights.keys())[:11])
    ]
    + [""]
    + [
        "\n" * ((i + 1) % 2) + f"{flight}".split("-")[1].split("a")[0]
        for i, flight in enumerate(list(circle_flights)[12:])
    ]
)

for x in xpos:
    ax.axvline(x, color="black")
ax.set_xticks(xtickpos, labels=xlabels)
ax.set_xlabel("")
ax.set_ylabel("altitude / m")

ax1 = ax.twiny()
ax1.set_xticks([xtickpos[11]], labels=["Transfer 20240906"])
ax1.set_xlim(ax.get_xlim())

ax.annotate(
    "West",
    xy=(230, 110),
    xycoords="figure points",
    xytext=(250, 118),
    fontsize=4,
    ha="center",
)
ax.annotate(
    "",
    xy=(220, 114),
    xytext=(280, 114),
    xycoords="figure points",
    fontsize=6,
    arrowprops={"arrowstyle": "<->", "linewidth": 0.2},
)
ax.annotate(
    "East",
    xy=(120, 110),
    xycoords="figure points",
    xytext=(100, 118),
    fontsize=4,
    ha="center",
)
ax.annotate(
    "",
    xy=(70, 114),
    xytext=(130, 114),
    xycoords="figure points",
    fontsize=6,
    arrowprops={"arrowstyle": "<->", "linewidth": 0.2},
)

# ax.set_ylim(0, 2500)

fig.savefig("../images/divergence.pdf", dpi=300, bbox_inches="tight")

# %%
# %% div lowest 2500 m
circle_flights = get_nb_circles_per_flight(ds_lev4)


plt.style.use("./beach.mplstyle")
fig, ax = plt.subplots(figsize=(24, 6))
im = (
    (ds_lev4.div)
    .sel(circle=slice(None, 43))
    .plot(
        cmap="coolwarm",
        ax=ax,
        y="altitude",
        center=0,
        vmin=-3e-5,
        vmax=3e-5,
        add_colorbar=False,
    )
)
fig.subplots_adjust(right=0.93)
cax = fig.add_axes([0.95, 0.15, 0.01, 0.7])
fig.colorbar(im, cax=cax, label="divergence / s-1", extend="both")
nb_circ = 0
ax.set_xlabel("")
ax.set_ylabel("Altitude / m")

ax.set_ylim(0, 2500)

fig.savefig("../images/divergence_east_low.png", bbox_inches="tight")
# %%
# %% div to mean lowest 2500 m
circle_flights = get_nb_circles_per_flight(ds_lev4)

cat = eurec4a.get_intake_catalog()
joanne = cat.dropsondes.JOANNE.level4.to_dask()


plt.style.use("./beach.mplstyle")
fig, ax = plt.subplots(figsize=(24, 6))
im = (joanne.D).plot(
    cmap="coolwarm",
    ax=ax,
    y="alt",
    center=0,
    vmin=-3e-5,
    vmax=3e-5,
    add_colorbar=False,
)
fig.subplots_adjust(right=0.93)
cax = fig.add_axes([0.95, 0.15, 0.01, 0.7])
fig.colorbar(im, cax=cax, label="divergence / s-1", extend="both")
ax.set_xlabel("")
ax.set_ylabel("Altitude / m")

ax.set_ylim(0, 2500)

fig.savefig("../images/divergence_joanne_low.png", bbox_inches="tight")
