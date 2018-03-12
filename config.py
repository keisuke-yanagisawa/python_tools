def read(configfile):
    config = {}
    with open(configfile) as fin:
        for line in fin:
            # treat strings as comment which are written after # in each line
            string = line[:line.find("#")]

            if len(string) == 0:
                continue

            aData = string.split()
            if len(aData) == 1:
                config[aData[0]] = ""
            else:
                config[aData[0]] = aData[1]
    return config


def write(path, config_dict):
    with open(path, "w") as fout:
        for item in config_dict.items():
            fout.write("%s %s\n" % item)
