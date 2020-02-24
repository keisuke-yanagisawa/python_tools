import configparser
import os


def assert_config(dat):
    None


def init_config():
    aDict = {
        "InputDir": {
        },
        "OutputDir": {
            "temporal": "/tmp/deepsitecrypto",
        },
        "Executables": {
            "blastp": "blastp",
            "makeblastdb": "makeblastdb",
        },
    }
    dat = configparser.ConfigParser()
    dat.read_dict(aDict)
    return dat


def read_config(configfile):
    dat = init_config()
    if not os.path.exists(configfile):
        print("[ERROR]", configfile, "is not exist")
        exit(1)
    dat.read(configfile)
    assert_config(dat)
    return dat
