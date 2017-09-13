### Manipulate compound files like mol2, sdf, pdb and so on.

import re
from rdkit import Chem

def separateMol2Blocks(string):

    # separate
    mol2blocks = re.compile("\n(?=@\<TRIPOS\>MOLECULE)").split(string)

    # add \n for all blocks except for the last block
    mol2blocks[-1] = mol2blocks[-1][:-1]
    return [mol2block+'\n' for mol2block in mol2blocks]
