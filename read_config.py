# -*- coding: utf-8 -*-


def read_config(configfile):
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
