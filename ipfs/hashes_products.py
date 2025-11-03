# %%
import ruamel.yaml
import sys
import os
import orcestra

sys.path.append("./")
sys.path.append("../")


# %% write ipfs hashes to file
yaml = ruamel.yaml.YAML(typ="rt")
tree = yaml.load(open("../../ipfs_tools/tree.yaml", "r"))
# %%
# config_path = "/Users/helene/Documents/Orcestra/playground/run_complete_orcestra/helene_complete_orcestra.cfg"
# config = data_utils.get_config(config_path)

product_path = "/Users/helene/Documents/Data/Dropsonde/dropsonde_data/products/"  # config["OPTIONAL"]["product_dir"]

tree["products"]["HALO"].setdefault("dropsondes", {})
if tree["products"]["HALO"]["dropsondes"] is None:
    tree["products"]["HALO"]["dropsondes"] = {}

level1 = orcestra.ipfs.ipfs_add(os.path.join(product_path, "Level_1"))

tree["products"]["HALO"]["dropsondes"]["Level_1"] = level1

# %%
# Save the updated tree back to the YAML file
with open("../../ipfs_tools/tree.yaml", "w") as file:
    yaml.dump(tree, file)

# %%
# ipfs dag export <cid> > <cid>.car
