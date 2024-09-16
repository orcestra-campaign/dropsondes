# %%
import subprocess
import ruamel.yaml
from tqdm import tqdm
import sys
import os

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

flight_id_template = config["OPTIONAL"]["path_to_l0_files"]
path_to_flight_ids = config["OPTIONAL"]["path_to_flight_ids"]
flight_ids = [f for f in os.listdir(path_to_flight_ids) if "HALO-" in f]
# %%

# add raw data to tree

# Ensure the structure exists and initialize empty dicts if they don't exist
tree["raw"]["HALO"].setdefault("dropsondes", {})
if tree["raw"]["HALO"]["dropsondes"] is None:
    tree["raw"]["HALO"]["dropsondes"] = {}

# add the hashes to the tree
for flight_id in tqdm(flight_ids):
    path_to_flight = os.path.join(
        path_to_flight_ids, flight_id_template.format(flight_id=flight_id)
    )
    raw_sonde = path2ipfs(path_to_flight)

    tree["raw"]["HALO"]["dropsondes"][f"{flight_id}"] = raw_sonde

# Save the updated tree back to the YAML file
with open("../../ipfs_tools/tree.yaml", "w") as file:
    yaml.dump(tree, file)

# %%
