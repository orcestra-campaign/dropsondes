import plots.settings as settings
import xarray as xr


def test_open_l3():
    xr.open_dataset(
        f"{settings.root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr",
        engine="zarr",
    )


def test_open_l4():
    xr.open_dataset(
        f"{settings.root}/products/HALO/dropsondes/Level_4/PERCUSION_Level_4.zarr",
        engine="zarr",
    )
