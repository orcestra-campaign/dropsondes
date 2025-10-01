# %%
import configparser

import copy
import numpy as np
import pydropsonde.pipeline
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
from pydropsonde.processor import Gridded
import pydropsonde
import itertools
import sys
from helper_products import calc_products, remove_from_one, iterate_circle
from helper_products import get_good, keep_good

sys.path.append("../")
from plots import settings  # noqa: E402


config = configparser.ConfigParser()
config.read("../orcestra_drop.cfg")

# %%

# %%
l3_ds = xr.open_dataset(
    f"{settings.root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr",
    engine="zarr",
)

gridded = Gridded(sondes={}, global_attrs={})
gridded.set_l3_ds(l3_ds.where((l3_ds["u_qc"] == 0) & (l3_ds["p_qc"] == 0), drop=True))
gridded.get_circle_times_from_segmentation(
    "https://orcestra-campaign.github.io/flight_segmentation/all_flights.yaml"
)
gridded.alt_dim = "altitude"
gridded.sonde_dim = "sonde"
gridded.create_interim_l4()


# %%
ref_int = False

circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles
good_circles = get_good(circles, thres=12)
circles = keep_good(circles, good_circles)
circles_play = copy.deepcopy(circles)


no_int_ref = iterate_circle(circles=circles_play, config=config, int=ref_int)
# %%
circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles
good_circles = get_good(circles, thres=12)
circles = keep_good(circles, good_circles)
circles_w = copy.deepcopy(circles)
weights_ref = iterate_circle(circles=circles_w, config=config, int=True)


# %%


var = "omega"

gap_alts = [500]  # , 7000]
gap_depths = [30, 300, 1500]  # 30, 1500, 1000]
sonde_ids = np.arange(0, 13)
result = {
    "int": {
        gap_alt: {
            gap_depth: {key: [] for key in circles.keys()} for gap_depth in gap_depths
        }
        for gap_alt in gap_alts
    },
    "no_int": {
        gap_alt: {
            gap_depth: {key: [] for key in circles.keys()} for gap_depth in gap_depths
        }
        for gap_alt in gap_alts
    },
}
for params in itertools.product(gap_alts, gap_depths, sonde_ids):
    print(params)
    gap_alt, gap_depth, gap_sonde = params
    try:
        gap_no_int = remove_from_one(
            gap_alt, gap_depth, gap_sonde, circles_play, config, int=ref_int
        )
    except IndexError:
        pass
    else:
        gap_no_int = calc_products(gap_no_int, config)
        gap_w = remove_from_one(
            gap_alt, gap_depth, gap_sonde, circles_w, config, int=True
        )
        gap_w = calc_products(gap_w, config)
        for key in gap_w.keys():
            result["int"][gap_alt][gap_depth][key].append(gap_w[key].circle_ds.copy())
            result["no_int"][gap_alt][gap_depth][key].append(
                gap_no_int[key].circle_ds.copy()
            )


# %%%

int_diff = {depth: [] for depth in gap_depths}
no_int_diff = {depth: [] for depth in gap_depths}

plt.style.use("../plots/beach.mplstyle")
sns.set_palette("bright")
cm = 1 / 2.54
colors = sns.color_palette("turbo", n_colors=len(result["int"][500][30].keys()))
fig, axes = plt.subplots(ncols=3, figsize=(12 * cm, 5.5 * cm))
for col, depth in enumerate(gap_depths):
    no_int_result = result["no_int"][500][depth]
    int_result = result["int"][500][depth]
    axes[col].set_title(f"gap depth {depth} m", fontsize=7)
    for idx, key in enumerate(int_result.keys()):
        int_ref = weights_ref[key].circle_ds
        no_ref = no_int_ref[key].circle_ds
        for int_sonde, no_int_sonde in zip(int_result[key], no_int_result[key]):
            axes[col].scatter(
                (int_sonde[var] - int_ref[var]) * 0.01 * (60 * 60),
                (no_int_sonde[var] - no_ref[var]) * 0.01 * (60 * 60),
                color=colors[idx],
                alpha=0.2,
                s=2,
                linewidth=0.5,
                rasterized=True,
            )
            int_diff[depth].append(
                (int_sonde[var] - int_ref[var]).values * 0.01 * (60 * 60)
            )
            no_int_diff[depth].append(
                (no_int_sonde[var] - no_ref[var]).values * 0.01 * (60 * 60)
            )
            """
            axes[col].scatter(
                (int_sonde[var] - int_ref[var]).median("altitude") * 0.01 * (60 * 60),
                (no_int_sonde[var] - no_ref[var]).median("altitude") * 0.01 * (60 * 60),
                color=colors[idx],
                s=2,
            )
            """

x = np.linspace(-5, 5, 20)
for ax in axes:
    ax.fill_betweenx(x, -x, x, color="lightgray", alpha=0.2)

limits = (-0.2, 0.2)  # (-0.1, 0.1)
axes[0].set_xlim(*limits)
axes[0].set_ylim(*limits)

limits = (-1.5, 1.5)  # (-1.3, 1.3)
axes[1].set_xlim(*limits)
axes[1].set_ylim(*limits)

limits = (-4.1, 4.1)
axes[2].set_xlim(*limits)
axes[2].set_ylim(*limits)


sns.despine(offset=5)
axes[1].set_xlabel("error for artificial gap with interpolation / hPa hr-1")
axes[0].set_ylabel("error for artificial gap / hPa hr-1 \n without interpolation ")
fig.tight_layout()
fig.savefig("../images/gap_sonde_500m.pdf", bbox_inches="tight", dpi=300)
# %%
for depth in gap_depths:
    print(depth)
    print("no int", np.nanmean(np.abs(np.array(no_int_diff[depth])).flatten()))
    print("+-", np.nanstd(np.abs(np.array(no_int_diff[depth])).flatten()))
    print("int", np.nanmean(np.abs(np.array(int_diff[depth])).flatten()))
    print("+-", np.nanstd(np.abs(np.array(int_diff[depth])).flatten()))
