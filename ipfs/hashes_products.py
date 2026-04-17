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

product_path = "/Users/helene/Documents/Data/Dropsonde/dropsonde_data/"  # config["OPTIONAL"]["product_dir"]

tree["products"]["HALO"].setdefault("dropsondes", {})
if tree["products"]["HALO"]["dropsondes"] is None:
    tree["products"]["HALO"]["dropsondes"] = {}

level1 = orcestra.ipfs.ipfs_add(os.path.join(product_path, "products/Level_1"))
print("l1 done")
level2 = orcestra.ipfs.ipfs_add(
    os.path.join(product_path, "products/Level_2/Level_2_ragged.zarr")
)
print("l2 done")
level0 = orcestra.ipfs.ipfs_add(os.path.join(product_path, "raw"))
print("l0 done")
level3 = orcestra.ipfs.ipfs_add(
    os.path.join(product_path, "products/Level_3/PERCUSION_Level_3.zarr")
)
level3qc = orcestra.ipfs.ipfs_add(
    os.path.join(product_path, "products/Level_3/PERCUSION_Level_3_qc.zarr")
)
print("l3 done")
level4 = orcestra.ipfs.ipfs_add(
    os.path.join(product_path, "products/Level_3/PERCUSION_Level_4.zarr")
)
print("l4 done")

tree["products"]["HALO"]["dropsondes"]["Level_1"] = level1
tree["products"]["HALO"]["dropsondes"]["Level_2"] = level2
tree["products"]["HALO"]["dropsondes"]["Level_3"]["Level_3"] = level3
tree["products"]["HALO"]["dropsondes"]["Level_3"]["Level_3_qc"] = level3qc
tree["products"]["HALO"]["dropsondes"]["Level_4"] = level4
tree["raw"]["HALO"]["dropsondes"] = level0


# %%
# Save the updated tree back to the YAML file
with open("../../ipfs_tools/tree.yaml", "w") as file:
    yaml.dump(tree, file)

# %%
# ipfs dag export <cid> > <cid>.car
