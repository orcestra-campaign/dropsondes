import copy
import configparser
from pydropsonde.circles import Circle
from pydropsonde.pipeline import get_args_for_function
import numpy as np


def iterate_Circle_method_over_dict_of_Circle_objects(
    circles: dict, functions: list, config: configparser.ConfigParser, **kwargs
) -> dict:
    for function in functions:
        new_dict = {}
        if not callable(function):
            function = getattr(Circle, function)
            kwargs = get_args_for_function(config, function)
        for key, value in circles.items():
            result = function(value, **kwargs)
            if result is not None:
                new_dict[key] = result

    return new_dict


def calc_products(circles, config):
    products = [
        "add_density",
        "apply_fit2d",
        "add_divergence",
        "add_vorticity",
        "add_omega",
        "add_circle_variables_to_ds",
        "add_wvel",
        # "add_regression_stderr",
        # "add_regression_stderr",
    ]
    iterate_Circle_method_over_dict_of_Circle_objects(circles, products, config=config)
    return circles


def get_xy_circles(circles, config):
    get_xy = ["interpolate_position", "get_xy_coords_for_circles", "drop_vars"]
    iterate_Circle_method_over_dict_of_Circle_objects(circles, get_xy, config=config)
    return circles


def interp_na(circles, interpolate, config):
    if interpolate:
        get_xy = [
            "interpolate_na_sondes",
            "extrapolate_na_sondes",
        ]
        iterate_Circle_method_over_dict_of_Circle_objects(
            circles, get_xy, config=config
        )
    return circles


def get_good(circles, thres=12):
    good_circles = []
    for name, circle in circles.items():
        ds = circle.circle_ds
        good_sondes = ds.where((ds["u_qc"] == 0) & (ds["p_qc"] == 0), drop=True).sizes[
            "sonde"
        ]

        if good_sondes >= thres:
            good_circles.append(name)
            print(name, good_sondes)
    return good_circles


def keep_good(circles, good_circles):
    for key in list(circles.keys()):
        if key not in good_circles:
            circles.pop(key)
        else:
            print(key)
    return circles


def iterate_circle(circles, config, int=False, w=None):
    circles_play = copy.deepcopy(circles)
    get_xy_circles(circles_play, config)
    interp_na(circles=circles_play, interpolate=int, config=config)
    calc_products(circles_play, config)
    return circles_play


def pipeline_like_iter(circles, config, int=False, w=None):
    circles_play = copy.deepcopy(circles)
    get_xy = [
        "get_xy_coords_for_circles",
        "drop_vars",
        "interpolate_na_sondes",
        "apply_fit2d",
        "add_divergence",
        "add_vorticity",
        "add_omega",
        "add_regression_stderr",
        "add_circle_variables_to_ds",
    ]
    iterate_Circle_method_over_dict_of_Circle_objects(
        circles_play, get_xy, config=config
    )
    return circles_play


def one_gap_one_sonde(circle, alt=1500, depth=500, sonde_id=2):
    ds = circle.circle_ds

    alt_mask = np.full(ds.u.shape, True)
    alt_mask[int(sonde_id), int(int(alt) / 10) : int((int(alt) + int(depth)) / 10)] = (
        False
    )

    for var in ["u", "v", "rh", "q", "ta", "theta", "x", "y"]:
        circle.circle_ds = circle.circle_ds.assign(
            {var: (ds[var].dims, ds[var].where(alt_mask).values, ds[var].attrs)}
        )
    return circle


def remove_from_one(gap_alt, gap_depth, gap_sonde, circles, config, int=False, w=None):
    print(gap_alt, gap_depth, gap_sonde)
    circles_play = copy.deepcopy(circles)
    get_xy_circles(circles_play, config)
    iterate_Circle_method_over_dict_of_Circle_objects(
        circles_play,
        [one_gap_one_sonde],
        config=None,
        alt=gap_alt,
        depth=gap_depth,
        sonde_id=gap_sonde,
    )

    interp_na(circles=circles_play, interpolate=int, config=config)
    return circles_play
