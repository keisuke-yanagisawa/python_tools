from commands import getoutput as gop

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



if __name__ == "__main__":
    import sys
    print size(sys.argv[1])
