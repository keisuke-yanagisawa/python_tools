# FingerPrint
import sys

from rdkit import Chem
from rdkit.Chem.Fingerprints import FingerprintMols
from rdkit import DataStructs

import compound

def fp_similarity(mol1, mol2):
    fps = [FingerprintMols.FingerprintMol(m) for m in (mol1, mol2)]
    return DataStructs.FingerprintSimilarity(fps[0], fps[1])

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print 'usage: python fingerprint_comparison.py file1.mol2 file2.mol2'
        exit(1)

    file1_suppl = compound.Mol2MolSupplier(sys.argv[1])
    file2_suppl = compound.Mol2MolSupplier(sys.argv[2])
    for mol1 in file1_suppl:
        if mol1 == None:
            continue
        for mol2 in file2_suppl:
            if mol2 == None:
                continue
            print mol1.GetProp('_Name'), mol2.GetProp('_Name'), fp_similarity(mol1, mol2)
            
