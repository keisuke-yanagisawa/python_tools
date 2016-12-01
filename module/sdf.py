from commands import getoutput as gop
import os.path
import gzip

def __isCompressed(file_name):
    _, ext = os.path.splitext(file_name)
    return ext == ".gz"

def size(file_name):
    """
    Counting the number of compounds in a sdf file.
    """
    
    command = "grep \$\$\$\$ | wc -l"
    if(__isCompressed(file_name)):
        file_read = "gzip -cd %s" % file_name 
    else:
        file_read = "cat %s" % file_name

    return int(gop(file_read+" | "+command))

def cpdsGenerator(file_name):
    """
    yielding a compound data string.
    """
    if(__isCompressed(file_name)):
        File = gzip.open(file_name)
    else:
        File = open(file_name)

    string = ""
    for line in File:
        string += line;
        if(line.startswith("$$$$")):
            yield string
            string = ""
    File.close()



if __name__ == "__main__":
    import sys
    print size(sys.argv[1])
    print len(list(cpdsGenerator(sys.argv[1])))
