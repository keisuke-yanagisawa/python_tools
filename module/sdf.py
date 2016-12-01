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

def getCpds(file_name, indices=None):
    """
    Getting compound string list, based on given indices list 
    Indices list is uniqued list, which has 0-origin indices.
    If indices is None, all compounds will listed.
    """

    if(indices is None):
        return list(cpdsGenerator(sys.argv[1]))

    #else:
    gen = cpdsGenerator(file_name)
    ret = []
    indices = sorted(indices)
    count = 0
    for index in indices:
        while(count < index):
            next(gen)
            count+=1
        ret.append(next(gen))
        count+=1
    gen.close()
    return ret
    

if __name__ == "__main__":
    import sys
    print size(sys.argv[1])
    print len(list(cpdsGenerator(sys.argv[1])))
    print getCpds(sys.argv[1], indices=[3])
