# %%
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.feature
import cartopy.crs as ccrs
import settings

from orcestra import get_flight_segments

# %%
l3 = f"{settings.root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr"
dsdrop = xr.open_dataset(l3, engine="zarr")  # .swap_dims({"sonde_id": "launch_time"})


# %%
def get_HALO_position(flight_id):
    root = settings.root
    dshalo = (
        xr.open_dataset(f"{root}/{flight_id}.zarr", engine="zarr")
        .reset_coords()
        .resample(time="1s")
        .mean()
    )
    return dshalo.lon, dshalo.lat


def get_halo_position_attitude(flight_id):
    root = settings.root
    return (
        xr.open_dataset(f"{root}/{flight_id}.zarr", engine="zarr")
        .reset_coords()
        .resample(time="1s")
        .mean()
        .load()
    )


# %%
meta = get_flight_segments()
flight_ids = [flight_id for flights in meta.values() for flight_id in flights]

# %%
segments = [
    {**s, "platform_id": platform_id, "flight_id": flight_id}
    for platform_id, flights in meta.items()
    for flight_id, flight in flights.items()
    for s in flight["segments"]
]
kinds = set(k for s in segments for k in s["kinds"])
# %%
events = [
    {**e, "platform_id": platform_id, "flight_id": flight_id}
    for platform_id, flights in meta.items()
    for flight_id, flight in flights.items()
    for e in flight["events"]
]

# %%
circle_ids = [s["segment_id"] for s in segments if "circle" in s["kinds"]]
print(f"Totel number of circles: {len(circle_ids)}")
atr_circle_ids = [
    s["segment_id"]
    for s in segments
    if ("circle" in s["kinds"] and "atr_coordination" in s["kinds"])
]
print(f"Number of ATR circles: {len(atr_circle_ids)}")
meteor_ids = [s["segment_id"] for s in segments if "meteor_coordination" in s["kinds"]]
print(f"Number of Meteor coordinations: {len(meteor_ids)}")
meteor_events = [e["event_id"] for e in events if "meteor_overpass" in e["kinds"]]
print(f"Number of Meteor overpasses: {len(meteor_events)}")
# %%


std_color = settings.colors.get("extra-sondes", "C0")
circle_color = settings.colors.get("halo-circles", "C1")
atr_color = settings.colors.get("atr", "C2")
meteor_color = settings.colors.get("meteor", "C3")

lon_min, lon_max, lat_min, lat_max = -65, -15, 0, 23  # -27, -19, 13, 20 (ATR area)
ds_st = dsdrop.swap_dims({"sonde": "sonde_time"})

plt.style.use("./beach.mplstyle")
size = 2
cm = 1 / 2.54
fig, ax = plt.subplots(
    figsize=(12 * cm, 5.5), subplot_kw=dict(projection=ccrs.PlateCarree())
)
gl = ax.gridlines(
    crs=ccrs.PlateCarree(),
    draw_labels=True,
    alpha=0.25,
    xlabel_style={"fontsize": 6},
    ylabel_style={"fontsize": 6},
)
gl.top_labels = False
gl.right_labels = False
ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor="black", facecolor="lightgrey")

ax.set_title(f"PERCUSION's {ds_st.sizes['sonde_time']} dropsondes")

ax.scatter(
    ds_st.aircraft_longitude,
    ds_st.aircraft_latitude,
    s=size,
    c=std_color,
    zorder=10,
)

count_atr_circles = 0
count_atr_sondes = 0
count_circles = 0
count_circle_sondes = 0
count_meteor_sondes = 0
count_other_sondes = 0

for s in segments:
    if "atr_coordination" in s["kinds"]:
        t = slice(s["start"], s["end"])
        ax.scatter(
            ds_st.aircraft_longitude.sel(sonde_time=t),
            ds_st.aircraft_latitude.sel(sonde_time=t),
            s=size,
            c=atr_color,
            zorder=90,
        )
        count_atr_circles += 1
        count_atr_sondes += ds_st.sel(sonde_time=t).sizes["sonde_time"]
    elif "circle" in s["kinds"]:
        t = slice(s["start"], s["end"])
        ax.scatter(
            ds_st.aircraft_longitude.sel(sonde_time=t),
            ds_st.aircraft_latitude.sel(sonde_time=t),
            s=size,
            c=circle_color,
            zorder=80,
        )
        sondes_in_circle = ds_st.sel(sonde_time=t).sizes["sonde_time"]
        if sondes_in_circle > 0:
            count_circles += 1
            count_circle_sondes += sondes_in_circle

for e in events:
    if "meteor_overpass" in e["kinds"]:
        t = slice(
            e["time"] - np.timedelta64(5, "m"), e["time"] + np.timedelta64(5, "m")
        )
        ax.scatter(
            ds_st.aircraft_longitude.sel(sonde_time=t),
            ds_st.aircraft_latitude.sel(sonde_time=t),
            s=size,
            c=meteor_color,
            zorder=100,
        )
        count_meteor_sondes += ds_st.sel(sonde_time=t).sizes["sonde_time"]

count_add_sondes = (
    ds_st.sizes["sonde_time"]
    - count_circle_sondes
    - count_atr_sondes
    - count_meteor_sondes
)

ax.scatter(
    [],
    [],
    s=size,
    c=circle_color,
    label=f"{count_circle_sondes + count_atr_sondes} sondes in {count_circles + count_atr_circles} circles in total",
)
ax.scatter(
    [],
    [],
    s=size,
    c=atr_color,
    label=f"{count_atr_sondes} sondes in {count_atr_circles} circles with ATR",
)
ax.scatter(
    [],
    [],
    s=size,
    c=meteor_color,
    label=f"{count_meteor_sondes} sondes close to METEOR",
)
ax.scatter(
    [],
    [],
    s=size,
    c=std_color,
    label=f"{count_add_sondes} additional sondes",
)

ax.legend(ncols=2)  # , title=f"Total number of sondes: {dsdrop.sizes["sonde"]}"
fig.savefig("../images/dropsonde_overview_map.pdf", dpi=300, bbox_inches="tight")

# %%
