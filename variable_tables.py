# %%
import xarray as xr
import pandas as pd
from plots import settings


# %%

l3_path = f"{settings.root}/products/HALO/dropsondes/Level_3"
l4_path = f"{settings.root}/products/HALO/dropsondes/Level_4"
l3 = xr.open_dataset(f"{l3_path}/PERCUSION_Level_3.zarr", engine="zarr")
l4 = xr.open_dataset(f"{l4_path}/PERCUSION_Level_4.zarr", engine="zarr")
# %%


def get_ds_vars(ds, other_ds=None):
    if other_ds is not None:
        other_ds = other_ds.variables
    else:
        other_ds = []
    return {
        var: {
            "variable": var.replace("_", "\_"),
            "units": ds[var].attrs.get("units", "").replace("_", "\_"),
            "standard\_name": ds[var].attrs.get("standard_name", "").replace("_", "\_"),
            "dimensions": " ".join(ds[var].dims),
        }
        for var in ds.data_vars
        if (var not in other_ds)
        and (not var.endswith("dx"))
        and (not var.endswith("dy"))
        and (not var.endswith("_mean"))
        and (not var.endswith("dx_std_error"))
        and (not var.endswith("dy_std_error"))
    }


def get_coords(ds):
    return {
        var: {
            "variable": var.replace("_", "\_"),
            "units": ds[var].attrs.get("units", "").replace("_", "\_"),
            "standard\_name": ds[var].attrs.get("standard_name", "").replace("_", "\_"),
            "dimensions": " ".join(ds[var].dims),
        }
        for var in ds.coords
    }


# %%
l3_records = get_ds_vars(l3)
l4_records = get_ds_vars(l4, l3)
# %%


l4_records.update(
    {
        "*\_mean": {
            "variable": "*\_mean",
            "units": "*",
            "standard\_name": "",
            "dimensions": "circle altitude",
        },
        "*\_d*dx": {
            "variable": "*\_d*dx",
            "units": "* m-1",
            "standard\_name": l4["u_dudx"]
            .attrs.get("standard_name", "")
            .replace(l4["u"].attrs.get("standard_name", ""), "*")
            .replace("_", "\_"),
            "dimensions": "circle altitude",
        },
        "*\_d*dy": {
            "variable": "*\_d*dy",
            "units": "* m-1",
            "standard\_name": l4["u_dudy"]
            .attrs.get("standard_name", "")
            .replace(l4["u"].attrs.get("standard_name", ""), "*")
            .replace("_", "\_"),
            "dimensions": "circle altitude",
        },
        "*\_d*dx_std\_error": {
            "variable": "*\_d*dx\_std\_error",
            "units": "* m-1",
            "standard\_name": l4["u_dudx_std_error"]
            .attrs.get("standard_name", "")
            .replace(l4["u"].attrs.get("standard_name", ""), "*")
            .replace("_", "\_"),
            "dimensions": "circle altitude",
        },
        "*\_d*dy_std\_error": {
            "variable": "*\_d*dy\_std\_error",
            "units": "* m-1",
            "standard\_name": l4["u_dudy_std_error"]
            .attrs.get("standard_name", "")
            .replace(l4["u"].attrs.get("standard_name", ""), "*")
            .replace("_", "\_"),
            "dimensions": "circle altitude",
        },
    }
)
for ds, name, records in [(l3, "l3", l3_records), (l4, "l4", l4_records)]:
    if name == "l4":
        other_ds = l3
    else:
        other_ds = None
    df = (
        pd.DataFrame.from_records(records)
        .transpose()
        .reset_index(drop=True)
        .sort_values("variable")
    )
    df_coord = (
        pd.DataFrame.from_records(get_coords(ds))
        .transpose()
        .reset_index(drop=True)
        .sort_values("variable")
    )

    df["object"] = "Variables"
    df_coord["object"] = "Coordinates"
    df_coord = df_coord.set_index(["object", "variable"])
    df = df.set_index(["object", "variable"])
    final = pd.concat([df, df_coord]).sort_index()
    final.to_latex(
        f"{name}_vars.tex",
        index=True,
        caption=f"BEACH Level {name[-1]} Variables",
        label=f"tab:l{name[-1]}vars",
    )
