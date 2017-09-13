### Manipulate compound files like mol2, sdf, pdb and so on.
import re
from rdkit import Chem

def separateMol2Blocks(string):

    # separate
    mol2blocks = re.compile("\n(?=@\<TRIPOS\>MOLECULE)").split(string)

    # add \n for all blocks except for the last block
    mol2blocks[-1] = mol2blocks[-1][:-1]
    return [mol2block+'\n' for mol2block in mol2blocks]

def MOL2BlockSupplier(filename):
    with open(filename) as fin:
        ForwardMol2BlockSupplier(fin)

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

def Mol2MolSupplier(filename, sanitize=True, removeHs=True):
    suppl = Mol2BlockSupplier(filename)
    for block in suppl:
        yield Chem.MolFromMol2Block(block, sanitize, removeHs)

def ForwardMol2MolSupplier(fileobj, sanitize=True, removeHs=True):
    suppl = ForwardMol2BlockSupplier(fileobj)
    for block in suppl:
        yield Chem.MolFromMol2Block(block, sanitize, removeHs)
