import argparse

import pandas as pd
import pybel

VERSION="0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate a csv file containing molecule information")
    parser.add_argument("-i", metavar="SDF", required=True, help="input sdf")
    parser.add_argument("-o", metavar="CSV", required=True, help="output csv")
    parser.add_argument("-fields", metavar="FIELD", nargs='+', required=True)
    parser.add_argument("-v,--version", action="version" ,version=VERSION)
    args = parser.parse_args()
    print(args.fields)

    # molwt, logp, data-r_i_docking_score

    data = []
    for mol in pybel.readfile("sdf", args.i):
        adict = {}
        for field in args.fields:
            if field == "molwt":
                adict[field] = mol.molwt
            elif field == "logp":
                adict[field] = mol.calcdesc(["LogP"])["LogP"]
            elif field == "title":
                adict[field] = mol.title
            else:
                adict[field] = mol.data[field]
        data.append(adict)

    pd.DataFrame.from_dict(data).to_csv(args.o, index=None)
        
