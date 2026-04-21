import plots.settings as settings
import xarray as xr


def test_open_l2():
    xr.open_dataset(
        f"ipfs://{settings.lev2}",
        engine="zarr",
    )


def test_open_l3():
    xr.open_dataset(
        f"ipfs://{settings.lev3}",
        engine="zarr",
    )


def test_open_l4():
    xr.open_dataset(
        f"ipfs://{settings.lev4}",
        engine="zarr",
    )
