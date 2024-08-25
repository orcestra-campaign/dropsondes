import xarray as xr
import matplotlib.pyplot as plt
from quicklooks import individual_sondes_profiles

flightdate = "20240811"

# Paths to the datasets
dp1 = "/Volumes/ORCESTRA/HALO-20240811a/dropsondes/Level_2/HALO-(AC)3_HALO_2024-08-11T14:47:35.000000_20240811_231430766_Level_2.nc"
dp2 = "/Volumes/ORCESTRA/HALO-20240811a/dropsondes/Level_2/HALO-(AC)3_HALO_2024-08-11T15:14:24.000000_20240811_231331380_Level_2.nc"
dp3 = "/Volumes/ORCESTRA/HALO-20240811a/dropsondes/Level_2/HALO-(AC)3_HALO_2024-08-11T16:30:40.000000_20240811_234140293_Level_2.nc"
dp4 = "/Volumes/ORCESTRA/HALO-20240811a/dropsondes/Level_2/HALO-(AC)3_HALO_2024-08-11T19:20:16.000000_20240811_233530214_Level_2.nc"

variables = ["u", "v", "ta", "rh", "p"]
units = ["m/s", "m/s", "K", "[0-1]", "Pa"]
location = ["in ITCZ", "south of ITCZ", "in ITCZ", "north of ITCZ"]

ds1 = xr.open_dataset(dp1)
ds2 = xr.open_dataset(dp2)
ds3 = xr.open_dataset(dp3)
ds4 = xr.open_dataset(dp4)

filepaths = [dp1, dp2, dp3, dp4]
datasets = [ds1, ds2, ds3, ds4]

# Plot
individual_sondes_profiles(
    flight_id=flightdate,
    filepath_list=filepaths,
    ds_list=datasets,
    loc_list=location,
    variables=variables,
    units=units,
)

# Save
plt.savefig(
    f"individual_dropsondes_PERCUSION_HALO_{flightdate}.png",
    bbox_inches="tight",
)
