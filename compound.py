### Manipulate compound files like mol2, sdf, pdb and so on.

import re

def separateMol2Blocks(string):
    return re.compile("\n(?=@\<TRIPOS\>MOLECULE)").split(string)
