# %%

import configparser

import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
from pydropsonde.processor import Gridded
import numpy as np
import numpy.polynomial.polynomial as poly

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
def get_autocorr_np(da, tau):
    vals = (da - da.mean("gpsalt")).values
    gh = vals[:, :-tau] * vals[:, tau:]
    axis = 1
    c0 = vals**2
    return (np.nansum(gh, axis=axis) / np.count_nonzero(~np.isnan(gh), axis=axis)) / (
        np.nansum(c0, axis=axis) / np.count_nonzero(~np.isnan(c0), axis=axis)
    )


def get_uncertainty(z, tau, da):
    vals = da.values
    gh = vals[:, :-tau] * vals[:, tau:]
    if np.count_nonzero(~np.isnan(gh)) == 0:
        print(tau)

    return z / np.sqrt(np.count_nonzero(~np.isnan(gh)))


# %%
ex = (
    l3_ds.where((l3_ds["u_qc"] == 0), drop=True)
    .where(l3_ds["gpsalt"] < 12000)
    .where(l3_ds["alt_near_gpsalt"] == 0)
)
shifts = np.arange(10, 5000, 10)
resu = {}
resu_std = {}
resv_std = {}
resv = {}

for shift in shifts:
    resu[shift] = get_autocorr_np(ex["u"], int(shift / 10))
    resv[shift] = get_autocorr_np(ex["v"], int(shift / 10))

# %%


def lin_fct(shifts, a, k):
    a = 0
    return a + k * shifts


def exp_fct(shifts, a, k):
    return np.exp(a + k * shifts)


def fit_lin_to_log(shifts, vals):
    vals = np.log(vals)
    a, k = poly.polyfit(shifts[~np.isnan(vals)], vals[~np.isnan(vals)], 1)
    return a, k


shifts = np.array(list(resu.keys()))
np_u = np.array([np.nanmean(resu[shift]) for shift in shifts])
np_v = np.array([np.nanmean(resv[shift]) for shift in shifts])

"""
np_u_std = []
np_v_std = []
for shift in shifts:
   np_u_std.append(get_uncertainty(1.96, int(shift/10), ex["u"]))
    np_v_std.append(get_uncertainty(1.96, int(shift/10), ex["v"]))
"""
np_u_std = [np.nanstd(resu[shift]) for shift in shifts]
np_v_std = [np.nanstd(resv[shift]) for shift in shifts]

exp_to = 50
fita_npu, fitk_npu = fit_lin_to_log(shifts[:exp_to], np_u[:exp_to])
fita_npv, fitk_npv = fit_lin_to_log(shifts[:exp_to], np_v[:exp_to])
# %%

colors = list(sns.color_palette("turbo"))
fig, ax = plt.subplots(figsize=(12, 6))
f = np.array  # np.log#
fitf = exp_fct  # lin_fct #
ax.scatter(shifts, f(np_u), color=colors[-1], label="u", zorder=2)

ax.scatter(shifts, f(np_v), color=colors[-2], label="v", zorder=2)
if f == np.array:
    ax.fill_between(
        shifts,
        np_u - np.array(np_u_std),
        np_u + np.array(np_u_std),
        color=colors[-1],
        alpha=0.2,
        zorder=1,
    )
    ax.fill_between(
        shifts,
        np_v - np.array(np_v_std),
        np_v + np.array(np_v_std),
        color=colors[-2],
        alpha=0.2,
        zorder=1,
    )

ax.plot(
    shifts[:exp_to],
    fitf(shifts[:exp_to], fita_npu, fitk_npu),
    color="black",
    zorder=3,
    label=r"$k \approx {}$".format(int(-1 / fitk_npu)),
)
ax.plot(
    shifts[:exp_to],
    fitf(shifts[:exp_to], fita_npv, fitk_npv),
    color="black",
    linestyle=":",
    label=r"$k \approx {}$".format(int(-1 / fitk_npv)),
    zorder=3,
)
ax.axhline(0, color="gray", zorder=1)

ax.axvline(1165, color="gray", zorder=1, linestyle=":")
ax.axvline(1958, color="gray", zorder=1)

ax.set_ylabel("Autocorrelation")
ax.set_xlabel(r"$\tau$ / m")
ax.legend()
sns.despine(offset=10)
fig.tight_layout()
fig.savefig("../images/autocorrelation.png")
# %%
ks = [fitk_npu, fitk_npv]
print([1 / k for k in ks])
print(np.mean([1 / k for k in ks]))

# %%
# %%
