# %%
import subprocess
import ruamel.yaml
import sys

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

# add raw data to tree

# Ensure the structure exists and initialize empty dicts if they don't exist
tree["products"]["HALO"].setdefault("dropsondes", {})


if tree["products"]["HALO"]["dropsondes"] is None:
    tree["products"]["HALO"]["dropsondes"] = {}
# add the hashes to the tree
product_sonde = path2ipfs(product_path)
tree["products"]["HALO"]["dropsondes"] = product_sonde

# Save the updated tree back to the YAML file
with open("../../ipfs_tools/tree.yaml", "w") as file:
    yaml.dump(tree, file)

# %%
