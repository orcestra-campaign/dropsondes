# %%
import subprocess
import ruamel.yaml
import sys
import os
from tqdm import tqdm

sys.path.append("./")
sys.path.append("../")
import droputils.data_utils as data_utils  # noqa: E402


# %%
def path2ipfs(path):
    ret = subprocess.run(
        [
            "/opt/homebrew/Cellar/ipfs/0.30.0/bin//ipfs",
            "add",
            "--recursive",
            "--hidden",
            "--quieter",
            "--raw-leaves",
            path,
        ],
        capture_output=True,
    )
    return ret.stdout.decode().strip()


# %% write ipfs hashes to file
yaml = ruamel.yaml.YAML(typ="rt")
tree = yaml.load(open("../../ipfs_tools/tree.yaml", "r"))
# %%
config_path = "/Users/helene/Documents/Orcestra/playground/run_complete_orcestra/complete_orcestra.cfg"
config = data_utils.get_config(config_path)

product_path = config["OPTIONAL"]["product_dir"]
# %%

# Ensure the structure exists and initialize empty dicts if they don't exist
tree["products"]["HALO"].setdefault("dropsondes", {})
if tree["products"]["HALO"]["dropsondes"] is None:
    tree["products"]["HALO"]["dropsondes"] = {}


# add product_data
level_dirs = ["Level_1", "Level_2"]
for level in level_dirs:
    print(level)
    tree["products"]["HALO"]["dropsondes"].setdefault(f"{level}", {})
    if tree["products"]["HALO"]["dropsondes"][f"{level}"] is None:
        tree["products"]["HALO"]["dropsondes"][f"{level}"] = {}
    fl_path = os.path.join(product_path, level)
    flight_ids = [f for f in sorted(os.listdir(fl_path)) if "HALO-" in f]
    for flight in tqdm(flight_ids):
        path_to_flight = os.path.join(fl_path, flight)
        lev_sonde = path2ipfs(path_to_flight)

        tree["products"]["HALO"]["dropsondes"][f"{level}"][f"{flight}"] = lev_sonde

level_dirs = ["Level_3", "Level_4"]
for level in tqdm(level_dirs):
    path2lev = os.path.join(product_path, level)
    lev_sonde = path2ipfs(path2lev)
    tree["products"]["HALO"]["dropsondes"][f"{level}"] = lev_sonde

# Save the updated tree back to the YAML file
with open("../../ipfs_tools/tree.yaml", "w") as file:
    yaml.dump(tree, file)

# %%
