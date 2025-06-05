# %%
import numpy as np
import xarray as xr
import pandas as pd
from orcestra import get_flight_segments
import fsspec
import re
from plots import settings
from datetime import timedelta


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
        "takeoff": flight["takeoff"],
        "landing": flight["landing"],
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
df = df.sort_values("takeoff")

# %%
total = {
    "flight ID": "Total",
    "takeoff": "",
    "landing": "",
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
entries = []
for key in meta["HALO"].keys():
    for entry in meta["HALO"][key]["segments"]:
        if ("atr_coordination" in entry["kinds"]) and ("circle" in entry["kinds"]):
            print(entry["segment_id"], entry["start"], entry["end"])
            entries.append(entry)
            print(entry["kinds"])

# %%


def get_atr_info(entry):
    start = entry["start"]
    end = entry["end"]
    id = entry["segment_id"]
    min_diff_to_atr_start = np.min(
        [np.abs(meta["ATR"][key]["takeoff"] - end) for key in meta["ATR"].keys()]
    )
    min_diff_to_atr_end = np.min(
        [np.abs(start - meta["ATR"][key]["landing"]) for key in meta["ATR"].keys()]
    )
    for key in meta["ATR"].keys():
        atr_start = meta["ATR"][key]["takeoff"]
        atr_end = meta["ATR"][key]["landing"]

        start_diff = np.abs(start - atr_end)
        end_diff = np.abs(atr_start - end)
        if np.abs(start_diff - min_diff_to_atr_end) < timedelta(minutes=5) or (
            np.abs(end_diff - min_diff_to_atr_start)
        ) < timedelta(minutes=5):
            # if ( timedelta(minutes=-6 * 60) < start_diff < timedelta(minutes=60)) or (timedelta(minutes=-6 * 60) < end_diff <timedelta(minutes=60)):
            return {
                "HALO circle ID": (id).replace("_", "\_"),
                "ATR flight ID": key,
                "ATR takeoff": atr_start,
                "ATR landing": atr_end,
                #                "HALO circle start": start,
                #                "HALO circle end": end,
                "Level 3 sondes": l3.where(
                    (l3.sonde_time > np.datetime64(start))
                    & (l3.sonde_time < np.datetime64(end)),
                    drop=True,
                ).sizes["sonde"],
                "Level 4 sondes": l4.swap_dims({"circle": "circle_id"})
                .sondes_per_circle.sel(circle_id=id)
                .values,
            }
    return {}


# %%
df = pd.DataFrame.from_records(map(get_atr_info, entries))

df.sort_values("HALO circle ID", inplace=True)
# %%
df.to_latex(
    "atr_stats.tex",
    index=False,
    caption="PERCUSION ATR coordination statistics showing the closest ATR flight to each atr-coordinated HALO circle and the number of sondes in Level 3 and Level 4 for those circles.",
    label="tab:atr_stats",
)
