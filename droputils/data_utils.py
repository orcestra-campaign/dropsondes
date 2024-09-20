import configparser


def get_config(config_file="../orcestra_drop.cfg"):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config
