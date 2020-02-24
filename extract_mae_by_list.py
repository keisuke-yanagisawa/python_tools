#!/usr/bin/python3

import argparse
import gzip
import os
import sys
if sys.version_info[0] == 2:
    from commands import getoutput
elif sys.version_info[0] == 3:
    from subprocess import getoutput
else:
    print("please run this code with Python 2 or Python 3")
    exit(1)

debug=False

MAE_HEADER="""{
 s_m_m2io_version
 :::
 2.0.0
}
"""

def detect_compound(fin, field):
    if field:
        field = field.split(",")  # for multicolumn
        name = [""]*len(field)
    else:
        field = ["s_m_title"]
        name = [""]
        
    st_offset = fin.tell()    
    line = fin.readline()

    is_compound_data = False
    section_header = False
    headers = []
    while line:
        if line.startswith("f_m_ct"):
            is_compound_data = True
            section_header = True
            
        elif line.strip().startswith(":::") and section_header:
            for header in headers:
                data = fin.readline().strip()
                if header in field:
                    name[field.index(header)] = data
            section_header = False
        elif line.startswith("}") and is_compound_data:
            break

        if section_header and not line.startswith("f_m_ct"):
            headers.append(line.strip())
        
        if not is_compound_data:
            st_offset = fin.tell()
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
        description="reorder compounds in a mae/maegz file according to a list")
    parser.add_argument("-i", dest="imae", help="path to input mae/maegz")
    parser.add_argument("-o", dest="omae", help="path to output mae/maegz")
    parser.add_argument("-l", dest="alist", help="path to a list file for reordering")
    parser.add_argument("-v", dest="rev", action="store_true", help="reverse selection")
    parser.add_argument("--field",
                        help="""field name for reordering.
                        TITLE will be used if it is not set.
                        the field MUST be unique.
                        Two or more fields can be set like 'hoge,fuga'.""")
    args = parser.parse_args()

    compound_dict = {}

    # 0. decompress input file if it is maegz file (because of its speediness)
    path_input = args.imae
    if os.path.splitext(args.imae)[1] == ".maegz":
        getoutput("gunzip -c {} > .temp.mae".format(args.imae))
        path_input = ".temp.mae"
    
    
    # 1. list up offset of filepointer
    fin = open(path_input)
    while True:
        if test_EOF(fin):
            break
        name, st_offset, ed_offset = detect_compound(fin, args.field)
        compound_dict[name] = (st_offset, ed_offset)
        if debug:
            print(name, compound_dict[name])
    fin.close()

    # 2. generate output
    fin  = open(path_input)
    fout = gzip.open(args.omae,"w") if os.path.splitext(args.omae)[1] == ".maegz" else open(args.omae, "w")
    fout.write(MAE_HEADER)
    fout.write("\n")
    with open(args.alist) as flist:
        if not args.rev:
            for line in flist:
                if line.strip() not in compound_dict:
                    continue
                offsets = compound_dict[line.strip()]
                fin.seek(offsets[0])
                fout.write(fin.read(offsets[1]-offsets[0]))
                fout.write("\n")
        else:
            for line in flist:
                if line.strip() in compound_dict:
                    del compound_dict[line.strip()]
            for key, value in compound_dict.items():
                offsets = value
                fin.seek(offsets[0])
                fout.write(fin.read(offsets[1]-offsets[0]))
                fout.write("\n")
    fin.close()
    fout.close()
