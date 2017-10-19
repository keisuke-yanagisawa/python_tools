def Mol2BlockSupplier(filename):
    with open(filename) as fin:
        suppl = ForwardMol2BlockSupplier(fin)
        for mol in suppl:
            yield mol

def ForwardMol2BlockSupplier(fileobj):
    mol2block = fileobj.readline()
    if not mol2block:
        print 'There is not any lines in the file: %s'%filename
        exit
        
    line = fileobj.readline()
    while line:
        if line.startswith('@<TRIPOS>MOLECULE'):
            yield mol2block
            mol2block = line
        else:
            mol2block = mol2block + line
        line = fileobj.readline()
    yield mol2block

class Mol2Data:
    """Compound representation of Mol2"""
    def __init__(self, string=None):
        self.filetype = 'mol2'
        self.setMol2String(string)
        
        
    def setMol2String(self, string=None):
        if string==None:
            self.name   = ""
            self.string = ""
        else:
            self.string = string
            self.name   = string.split("\n")[1].strip()

    def __str__(self):
        return self.string

    

if __name__ == "__main__": 
    import sys
    
    suppl = Mol2BlockSupplier(sys.argv[1])
    for string in suppl:
        temp = Mol2Data(string)
        print temp.name
