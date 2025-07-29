# %%
import numpy as np
import xarray as xr
import pandas as pd
from orcestra import get_flight_segments
import fsspec
import re
from plots import settings


meta = get_flight_segments()


# %%
def fsglob(pattern):
    schema = pattern.split(":")[0]
    fs = fsspec.filesystem(schema)
    return fs.glob(pattern)


def fsls(path):
    schema = path.split(":")[0]
    fs = fsspec.filesystem(schema)
    return fs.ls(path, detail=False)


# %%
root = settings.root
l0_path = f"{root}/raw/HALO/dropsondes"
l1_path = f"{root}/products/HALO/dropsondes/Level_1"
l2_path = f"{root}/products/HALO/dropsondes/Level_2"
l3_path = f"{root}/products/HALO/dropsondes/Level_3"
l4_path = f"{root}/products/HALO/dropsondes/Level_4"
# %%
l3 = xr.open_dataset(f"{l3_path}/PERCUSION_Level_3.zarr", engine="zarr")
l4 = xr.open_dataset(f"{l4_path}/PERCUSION_Level_4.zarr", engine="zarr")


# %%
def get_flight_info(flight_id):
    flight = meta["HALO"][flight_id]
    s_id = set(s["segment_id"] for s in flight["segments"])
    flight_l3 = l3.where(lambda ds: ds.flight_id == flight_id, drop=True)
    ci = [i for i, c_id in enumerate(l4.circle_id.values) if c_id in s_id]
    if ci:
        sonde_bounds = np.concatenate([[0], np.cumsum(l4.sondes_per_circle)]).tolist()
        sonde_slices = [
            slice(a, b) for a, b in zip(sonde_bounds[:-1], sonde_bounds[1:])
        ]
        sonde_idx = np.arange(l4.sizes["sonde"])
        sonde_i = np.concatenate([sonde_idx[sonde_slices[c]] for c in ci])
        l4_sondes = l4.isel(circle=ci, sonde=sonde_i).sizes["sonde"]
        l4_circles = len(ci)
    else:
        l4_sondes = 0
        l4_circles = 0

    return {
        "flight ID": flight_id,
        "date": flight["date"],
        "flight time": str(flight["takeoff"].strftime("%H:%M:%S"))
        + "-"
        + str(flight["landing"].strftime("%H:%M:%S")),
        # "landing": flight["landing"].strftime("%H:%M:%S"),
        "Level 0": len(
            [
                fname
                for fname in fsglob(f"{l0_path}/{flight_id}/D*")
                if re.match(r"^(?:.*/)?D(?:[0-9]{8}_)?[0-9]{6}\.[1-8]$", fname)
            ]
        ),
        "Level 1": len(fsls(f"{l1_path}/{flight_id}")),
        "Level 2": len(fsls(f"{l2_path}/{flight_id}")),
        "Level 3": flight_l3.sizes["sonde"],
        "Level 4": l4_sondes,
        "circles": l4_circles,
    }


# %%
df = pd.DataFrame.from_records(map(get_flight_info, set(l3.flight_id.values)))
df = df.sort_values("date")

# %%
total = {
    "flight ID": "Total",
    "date": "",
    "flight time": "",
    # "landing": "",
    "Level 0": df["Level 0"].sum(),
    "Level 1": df["Level 1"].sum(),
    "Level 2": df["Level 2"].sum(),
    "Level 3": df["Level 3"].sum(),
    "Level 4": df["Level 4"].sum(),
    "circles": df["circles"].sum(),
}
df = pd.concat([df, pd.DataFrame(total, index=[-1])])
df
# %%
df.to_latex(
    "sonde_stats.tex",
    index=False,
    caption="PERCUSION dropsonde statistics showing the number of sondes per flight and processing level.",
    label="tab:sonde_stats",
)
# %%
atr_circle_segments = []
for halo_flight in meta["HALO"].keys():
    for entry in meta["HALO"][halo_flight]["segments"]:
        if ("atr_coordination" in entry["kinds"]) and ("circle" in entry["kinds"]):
            print(entry["segment_id"], entry["start"], entry["end"])
            atr_circle_segments.append(entry)
            print(entry["kinds"])


# %%
def atr_flight_for_circle(circle):
    potential_flights = []
    for key in meta["ATR"].keys():
        flight = meta["ATR"][key]
        if circle["start"].date() == flight["date"]:
            potential_flights.append(flight)
            # print(flight["flight_id"], flight["takeoff"], flight["landing"])
    if len(potential_flights) == 0:
        print("No ATR flight found for circle", circle["segment_id"])
        return None
    elif len(potential_flights) == 1:
        return potential_flights[0]
    elif len(potential_flights) > 1:
        circle_ref_time = circle["start"] + (circle["end"] - circle["start"]) / 2
        flight_ref_time = [
            flight["takeoff"] + (flight["landing"] - flight["takeoff"]) / 2
            for flight in potential_flights
        ]
        flight_ind = np.argmin([np.abs(circle_ref_time - f) for f in flight_ref_time])
        return potential_flights[flight_ind]


for circle in atr_circle_segments:
    print(
        circle["segment_id"],
        circle["start"].strftime("%H:%M:%S"),
        circle["end"].strftime("%H:%M:%S"),
    )
    flight = atr_flight_for_circle(circle)
    print(
        flight["flight_id"],
        flight["takeoff"].strftime("%H:%M:%S"),
        flight["landing"].strftime("%H:%M:%S"),
    )
    print("--------")

# %%


def get_atr_info(circle):
    flight = atr_flight_for_circle(circle)
    return {
        "flight ID": flight["flight_id"],
        "flight date": flight["date"],
        "flight time": f"{flight['takeoff'].strftime('%H:%M:%S')}-{flight['landing'].strftime('%H:%M:%S')}",
        "Level 3 sondes": l3.where(
            (l3.sonde_time > np.datetime64(circle["start"]))
            & (l3.sonde_time < np.datetime64(circle["end"])),
            drop=True,
        ).sizes["sonde"],
        "Level 4 sondes": l4.swap_dims({"circle": "circle_id"})
        .sondes_per_circle.sel(circle_id=circle["segment_id"])
        .values,
        "HALO circle ID": circle["segment_id"].replace("_", "\_"),
    }


# %%
df = pd.DataFrame.from_records(map(get_atr_info, atr_circle_segments))

df.sort_values("flight ID", inplace=True)
# %%
df.to_latex(
    "atr_stats.tex",
    index=False,
    caption="PERCUSION ATR coordination statistics showing the closest ATR flight to each atr-coordinated HALO circle and the number of sondes in Level 3 and Level 4 for those circles.",
    label="tab:atr_stats",
)
