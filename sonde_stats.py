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
    caption="PECUSION dropsonde statistics showing the number of sondes per flight and processing level.",
    label="tab:sonde_stats",
)
