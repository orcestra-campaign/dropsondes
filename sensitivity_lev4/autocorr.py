# %%

import configparser

import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
from pydropsonde.processor import Gridded


config = configparser.ConfigParser()
config.read("../orcestra_drop.cfg")

# %%


root = "ipfs://Qmbx6KSDfviFFi7f5XXQLB6MSTPhWnN1rNkCCKhyhaa7CA"
l3_ds = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3_qc/PERCUSION_Level_3.zarr", engine="zarr"
)

gridded = Gridded(sondes={}, global_attrs={})
gridded.set_l3_ds(l3_ds)
gridded.get_circle_times_from_segmentation(
    "https://orcestra-campaign.github.io/flight_segmentation/all_flights.yaml"
)
gridded.alt_dim = "gpsalt"


# %%
def get_autocorr(da, shift, shift_dim="gpsalt"):
    da_shift = da.assign_coords({shift_dim: da[shift_dim] + shift})
    return xr.corr(da, da_shift, dim=shift_dim)


ex = (
    l3_ds.where((l3_ds["u_qc"] == 0), drop=True)
    .where(l3_ds["gpsalt"] < 12000)
    .where(l3_ds["alt_near_gpsalt"] == 0)
)
shifts = [
    5,
    10,
    50,
    100,
    300,
    500,
    1000,
    1500,
    2000,
    2500,
    3000,
    3500,
    4000,
    4500,
    5000,
]
resu = {}
resv = {}
for shift in shifts:
    resu[shift] = get_autocorr(ex["u"], shift)
    resv[shift] = get_autocorr(ex["v"], shift)
# %%
colors = list(sns.color_palette("turbo"))
fig, ax = plt.subplots(figsize=(12, 6))
umean = "u mean"
umedian = "u median"
vmean = "v mean"
vmedian = "v median"
for shift in shifts:
    if shift > 5:
        umean = ""
        umedian = ""
        vmean = ""
        vmedian = ""
    ax.scatter(shift, resu[shift].median(), color=colors[1], label=umedian)

    ax.scatter(shift, resv[shift].median(), color=colors[2], label=vmedian)
    ax.errorbar(
        shift,
        resv[shift].mean(),
        yerr=resv[shift].std(ddof=1, skipna=True),
        color=colors[-2],
        marker="o",
        label=vmean,
    )
    ax.errorbar(
        shift,
        resu[shift].mean(),
        yerr=resu[shift].std(ddof=1, skipna=True),
        color=colors[-1],
        marker="o",
        label=umean,
    )

ax.legend()
ax.axhline(0, color="grey", alpha=0.5)
ax.set_ylabel("Autocorrelation")
ax.set_xlabel("shift / m")
sns.despine(offset=10)
# fig.savefig("../images/autocorrelation.png")
