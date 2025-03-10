# %%
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.feature
import cartopy.crs as ccrs

from orcestra import get_flight_segments

# %%
l3 = "ipns://latest.orcestra-campaign.org/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr"
dsdrop = xr.open_dataset(l3, engine="zarr")#.swap_dims({"sonde_id": "launch_time"})

# %%
def get_HALO_position(flight_id):
    root = "ipfs://QmTGwJ6VAn2FTiwsXaAA4BUA82RN2zQPBEJ8rpWrviW4c3"
    dshalo = xr.open_dataset(f"{root}/{flight_id}.zarr", engine="zarr").reset_coords().resample(time="1s").mean()
    return dshalo.lon, dshalo.lat

def get_halo_position_attitude(flight_id):
    root = "ipns://latest.orcestra-campaign.org/products/HALO/position_attitude"
    return (xr.open_dataset(f"{root}/{flight_id}.zarr", engine="zarr")
            .reset_coords().resample(time="1s").mean().load())
# %%
meta = get_flight_segments()
flight_ids = [flight_id
              for flights in meta.values()
              for flight_id in flights]

# %%
segments = [{**s,
             "platform_id": platform_id,
             "flight_id": flight_id
            }
            for platform_id, flights in meta.items()
            for flight_id, flight in flights.items()
            for s in flight["segments"]
           ]
kinds = set(k for s in segments for k in s["kinds"])
# %%
events = [{**e,
             "platform_id": platform_id,
             "flight_id": flight_id
            }
            for platform_id, flights in meta.items()
            for flight_id, flight in flights.items()
            for e in flight["events"]
           ]

# %%
circle_ids = [s["segment_id"] for s in segments if "circle" in s["kinds"]]
print(f"Totel number of circles: {len(circle_ids)}")
atr_circle_ids = [s["segment_id"] for s in segments if ("circle" in s["kinds"] and "atr_coordination" in s["kinds"])]
print(f"Number of ATR circles: {len(atr_circle_ids)}")
meteor_ids = [s["segment_id"] for s in segments if "meteor_coordination" in s["kinds"]]
print(f"Number of Meteor coordinations: {len(meteor_ids)}")
meteor_events = [e["event_id"] for e in events if "meteor_overpass" in e["kinds"]]
print(f"Number of Meteor overpasses: {len(meteor_events)}")
# %%
def kinds2color(kinds):
    if "circle" and "atr_coordination" in kinds:
        return "C2"
    if "circle" in kinds:
        return "C1"
    if "ec_track" in kinds:
        return "C3"
    return "C0"
# %%
lon_min, lon_max, lat_min, lat_max = -65, -15, 0, 23 #-27, -19, 13, 20 (ATR area)
ds_st = dsdrop.swap_dims({"sonde": "sonde_time"})

plt.figure(figsize = (10.5, 6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
#ax.coastlines(alpha=1.0)
ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor='black')
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, alpha = 0.25)
plt.title(f"PERCUSION's {ds_st.sizes["sonde_time"]} dropsondes")

plt.scatter(ds_st.aircraft_longitude,
            ds_st.aircraft_latitude,
            s=8, c="C0", zorder=10)

count_atr_circles = 0
count_atr_sondes = 0
count_circles = 0
count_circle_sondes = 0
count_meteor_sondes = 0
count_other_sondes = 0

for s in segments:
    if "atr_coordination" in s["kinds"]:
        t = slice(s["start"], s["end"])
        #ax.plot(ds.lon.sel(time=t), ds.lat.sel(time=t), c="C4", lw=3, alpha=1)
        plt.scatter(ds_st.aircraft_longitude.sel(sonde_time=t),
                    ds_st.aircraft_latitude.sel(sonde_time=t),
                    s=8, c="C4", zorder=90)
        count_atr_circles += 1
        count_atr_sondes += ds_st.sel(sonde_time=t).sizes["sonde_time"]
    elif "circle" in s["kinds"]:
        t = slice(s["start"], s["end"])
        #ax.plot(ds.lon.sel(time=t), ds.lat.sel(time=t), c="C1", lw=3, alpha=1)
        plt.scatter(ds_st.aircraft_longitude.sel(sonde_time=t),
                    ds_st.aircraft_latitude.sel(sonde_time=t),
                    s=8, c="C1", zorder=80)
        sondes_in_circle = ds_st.sel(sonde_time=t).sizes["sonde_time"]
        if sondes_in_circle > 0:
            count_circles += 1
            count_circle_sondes += sondes_in_circle

for e in events:
    if "meteor_overpass" in e["kinds"]:
        t = slice(e["time"] - np.timedelta64(5, "m"), e["time"] + np.timedelta64(5, "m"))
        #ax.plot(ds.lon.sel(time=t), ds.lat.sel(time=t), c="C2", lw=3, alpha=1)
        plt.scatter(ds_st.aircraft_longitude.sel(sonde_time=t),
                    ds_st.aircraft_latitude.sel(sonde_time=t),
                    s=8, c="C2", zorder=100)
        count_meteor_sondes += ds_st.sel(sonde_time=t).sizes["sonde_time"]

count_add_sondes = ds_st.sizes["sonde_time"] - count_circle_sondes - count_atr_sondes - count_meteor_sondes

plt.scatter([], [], s=8, c="C1", label=f"{count_circle_sondes+count_atr_sondes} sondes in {count_circles+count_atr_circles} circles in total")
plt.scatter([], [], s=8, c="C4", label=f"{count_atr_sondes} sondes in {count_atr_circles} circles with ATR")
plt.scatter([], [], s=8, c="C2", label=f"{count_meteor_sondes} sondes close to METEOR")
plt.scatter([], [], s=8, c="C0", label=f"{count_add_sondes} additional sondes")

plt.legend(ncols=2)#, title=f"Total number of sondes: {dsdrop.sizes["sonde"]}"
plt.savefig("dropsonde_overview_map.png", dpi=300, bbox_inches="tight")
# %%
