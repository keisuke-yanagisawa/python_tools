from rdkit.Chem import AllChem
from rdkit.Chem import Draw
from rdkit import Chem
from itertools import chain

def react_all(mol, reaction):
    prev = (mol,)
    now = __react_1step(mol, reaction)
    while (len(prev) != len(now)):
        prev = now
        now = list(chain.from_iterable([__react_1step(mol, reaction) for mol in prev]))

    return now;
    
def __react_1step(mol, reaction):
    Chem.GetSSSR(mol);
    temp = reaction.RunReactants((mol,))
    if(len(temp) == 0):
        return (mol,)
    else:
        return temp[0];

smarts=AllChem.ReactionFromSmarts("[N:1][C&!R:2](=[O:3])[N:4]>>[N:1].[C&!R:2](=[O:3]).[N:4]")
hoge = AllChem.MolFromSmiles("C(=O)NCC1C(=O)ONCOC1CC(=O)OCCNC(=O)N1CCCC1")
img = Draw.MolToImage(hoge);
img.save("hoge.png")
print [Chem.MolToSmiles(x) for x in react_all(hoge, smarts)]
#
#while True:
#    temp = smarts.RunReactants(mols)[0]
#    print [Chem.MolToSmiles(x) for x in temp]
#    if len(temp) == 0:
#        break
#    else:
#        mols = temp
