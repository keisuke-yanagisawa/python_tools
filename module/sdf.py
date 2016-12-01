from commands import getoutput as gop
import gzip

def size(file_name, compressed=False):
    """
    Counting the number of compounds in a sdf file.
    """
    
    command = "grep \$\$\$\$ | wc -l"
    if(compressed):
        file_read = "gzip -cd %s" % file_name 
    else:
        file_read = "cat %s" % file_name

    return gop(file_read+" | "+command)

def cpdsGenerator(file_name, compressed=False):
    if(compressed):
        File = gzip.open(file_name)
    else:
        File = open(file_name)

    string = ""
    for line in File:
        string += line;
        if(line.startswith("$$$$")):
            yield string
            string = ""



if __name__ == "__main__":
    import sys
    print size(sys.argv[1])
    print len(list(cpdsGenerator(sys.argv[1])))
