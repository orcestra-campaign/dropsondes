from quickgrid import grid_together, derived_products
from plotting import all_quicklook_plots
from datetime import datetime

flight_time = datetime(2024, 8, 22, 12, 0, 0)
flight_id = flight_time.strftime("%Y%m%d")

# Flight directory
dropsonde_dir = f"/Users/ninarobbins/Desktop/PhD/ORCESTRA/HALO-DATA/{flight_id}"

# Flight dataset

dropsonde_ds = grid_together(dropsonde_dir)
dropsonde_ds = derived_products(dropsonde_ds)

# Plots
all_quicklook_plots(dropsonde_ds, flight_id)
