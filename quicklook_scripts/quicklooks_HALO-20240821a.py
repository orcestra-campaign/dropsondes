from quickgrid import grid_together, derived_products
from plotting import all_quicklook_plots, profiles_from_ds
from datetime import datetime

flight_time = datetime(2024, 8, 21, 0, 0, 0)
flight_id = flight_time.strftime("%Y%m%d")

# Flight directory
dropsonde_dir = f"/Volumes/ORCESTRA/HALO-{flight_id}a/dropsondes"

# Grid flight dataset from Level 1
dropsonde_ds = grid_together(dropsonde_dir)
dropsonde_ds = derived_products(dropsonde_ds)

# Plots for all sondes
all_quicklook_plots(dropsonde_ds, flight_id)

# Plots for individual circles
circle_start_times = [
    "2024-08-11T14:15",
    "2024-08-11T16:00",
    "2024-08-11T17:25",
    "2024-08-11T19:05",
]
circle_end_times = [
    "2024-08-11T15:30",
    "2024-08-11T17:20",
    "2024-08-11T19:00",
    "2024-08-11T21:00",
]
circle_names = ["circle_south", "circle_middle", "circle_north", "circle_atr"]

for i in range(circle_start_times):
    circle_ds = dropsonde_ds.sel(
        launch_time=slice(circle_start_times[i], circle_end_times)
    )
    profiles_from_ds(circle_ds, flight_id)
