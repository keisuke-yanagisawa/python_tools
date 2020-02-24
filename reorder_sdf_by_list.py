#!/usr/bin/python3

import argparse

debug=False

class filedata:

    def __init__(self, filename, st_offset, ed_offset):
        if ed_offset < st_offset:
            raise ValueError("reversed order of file offsets : %s %d %d" % (filename, st_offset, ed_offset))
        self.filename = filename
        self.st = st_offset
        self.ed = ed_offset

    def read(self):
        with open(self.filename) as fin:
            fin.seek(self.st)
            s = fin.read(self.ed - self.st)
        return s

def detect_compound(fin, field):
    if field:
        field = field.split(",")  # for multicolumn
        name = [""]*len(field)
    else:
        name = [""]
    st_offset = fin.tell()

    line = fin.readline()
    if not field:
        name[0] = line.strip()
    while line:
        if debug:
            print(line)
            
        if field:
            for i, key in enumerate(field):
                if line.startswith("> <%s>" % key):
                    name[i] = fin.readline().strip()
        if line.startswith("$$$$"):
            break
        line = fin.readline()
    ed_offset = fin.tell()
    return ",".join(name), st_offset, ed_offset


def test_EOF(f):
    offset = f.tell()
    b = f.read(1)
    f.seek(offset)
    return (b == '')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="reorder compounds in a sdf file according to a list")
    parser.add_argument("-i", dest="isdf", help="path to input sdf", required=True)
    parser.add_argument("-o", dest="osdf", help="path to output sdf", required=True)
    parser.add_argument("-l", dest="alist", help="path to a list file for reordering", required=True)
    parser.add_argument("--ignore-notfound", action="store_true")
    parser.add_argument("--field",
                        help="""field name for reordering.
                        TITLE will be used if it is not set.
                        the field MUST be unique.
                        Two or more fields can be set like 'hoge,fuga'.""")
    args = parser.parse_args()

    compound_dict = {}
    # 1. list up offset of filepointer
    with open(args.isdf) as fin:
        while True:
            if test_EOF(fin):
                break
            name, st_offset, ed_offset = detect_compound(fin, args.field)
            compound_dict[name] = filedata(args.isdf, st_offset, ed_offset)
            if debug:
                print(name, compound_dict[name])

    # 2. generate output
    with open(args.alist) as flist:
        with open(args.osdf, "w") as fout:
            for line in flist:
                if line.strip() not in compound_dict:
                    if not args.ignore_notfound:
                        print("[ERROR] record is missing: %s"%line.strip())
                        exit(1)
                    else:
                        print("[NOTE] record is missing: %s"%line.strip()) 
                else:
                    fout.write(compound_dict[line.strip()].read())
