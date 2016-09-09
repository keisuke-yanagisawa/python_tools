from rdkit.Chem import AllChem
from rdkit.Chem import Draw
from rdkit.Chem import Recap
from rdkit import Chem

sdsuppl = Chem.SDMolSupplier("96_p0.0.sdf")
results = {}
for mol in sdsuppl:
    res = Recap.RecapDecompose(mol).GetLeaves()
    if len(res.keys()) == 0: # there is no bond to decompose
        res = {Chem.MolToSmiles(mol): mol};
        
    results.update(res)
    print Chem.MolToSmiles(mol), res.keys()

print results.keys()
print len(results.keys())
