import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split .mol2 file into N entries each.")
    parser.add_argument("mol2file", help="filename you want to split")
    parser.add_argument("-n", dest="N", metavar="N", type=int, default=10000, help="the max number of entries in each splitted file. default=10000")
    parser.add_argument("-v", dest="verbose", action="store_true", help="explain what is being done")
    args = parser.parse_args()

    file = args.mol2file
    filename, file_extension = os.path.splitext(file)
    N = args.N
    
    string = ""
    count = 0;
    for line in open(file):
        if(line.startswith("@<TRIPOS>MOLECULE")):
            count += 1
            if(count % N == 0):
                output = filename+"_"+str(count/N)+".mol2"
                file = open(output, "w");
                file.write(string);
                file.close();
                if args.verbose:
                    print("output : %s" % output)
                string = "";
        string += line;
            
    if(count%N != 0):
        file = open(filename+"_"+str(count/N + 1)+".mol2", "w");
        file.write(string);
        file.close();

    print("%d compounds are divided into %d files." % (count, count/N+1 if count%N!=0 else count/N))
