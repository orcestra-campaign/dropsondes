import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))
from quickgrid import grid_together, derived_products
from plotting import all_quicklook_plots
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
