import configparser
import os
from datetime import datetime, date, time
import numpy as np
from matplotlib.path import Path
import droputils.rough_segments as segments


def get_config(config_file="../orcestra_drop.cfg"):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def get_l3_path(config, flight_id="20240811", platform="HALO"):
    """
    get l3 filename for a flight from config file
    """
    l3_file = os.path.join(
        config["processor.Gridded.get_l3_dir"]["l3_dir"],
        config["processor.Gridded.get_l3_filename"]["l3_filename_template"].format(
            platform=platform
        ),
    )
    return l3_file


def get_circle_data(ds, flight_id="20240811"):
    """
    get a dictionary of circle data for one flight
    """
    flight_date = date.fromisoformat(flight_id)
    circles = {
        circle: {
            "start_time": np.datetime64(
                datetime.combine(
                    flight_date, time.fromisoformat(segments.starts[flight_id][circle])
                )
            ),
            "end_time": np.datetime64(
                datetime.combine(
                    flight_date, time.fromisoformat(segments.ends[flight_id][circle])
                )
            ),
        }
        for circle in segments.starts[flight_id].keys()
    }
    ds_c = {}
    for circle in list(circles.keys()):
        try:
            ds_c[circle] = ds.where(
                ds["launch_time_(UTC)"].astype("datetime64")
                > circles[circle]["start_time"],
                drop=True,
            ).where(
                ds["launch_time_(UTC)"].astype("datetime64")
                < circles[circle]["end_time"],
                drop=True,
            )
        except ValueError:
            print(f"No sondes for circle {circle}. It is omitted")

    return ds_c


def sel_sub_domain(
    ds, polygon, item_var="sonde", lon_var="launch_lon", lat_var="launch_lat"
):
    """
    select points from dataset that lie within the polygon
    """
    points = np.column_stack([ds[lon_var].values, ds[lat_var].values])
    inside = Path(polygon).contains_points(points)
    return ds.sel(**{item_var: inside})


def get_circle_id_for_sondes(ds):
    return ds.assign(
        circle_id_sonde=(
            ("sonde"),
            np.concat(
                [
                    np.repeat(
                        ds.sel(circle=circle).circle_id.values,
                        ds.sel(circle=circle).sondes_per_circle.values,
                    )
                    for circle in ds.circle
                ]
            ),
        )
    )


def assign_circle_var_to_sondes(ds, var):
    return ds.assign(
        {
            f"{var}_sonde": (
                ("sonde", "altitude"),
                np.concat(
                    [
                        np.stack(
                            ([ds.sel(circle=circle)[var].values],)
                            * int(ds.sel(circle=circle).sondes_per_circle.values),
                            axis=0,
                        ).squeeze()
                        for circle in ds.circle
                    ],
                    axis=0,
                ),
            ),
        }
    )
