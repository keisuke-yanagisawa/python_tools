import pybel

def estimate_volume(obmol):
    """
    Calculate estimated volume of a compound.
    Reference is below:
    Zhao YH, et al., "Fast calculation of van der Waals volume as a sum of 
    atomic and bond contributions and its application to drug compounds", 
    The Journal of Organic Chemistry, 68(19), 7368--7373, 2003.
    """

    #making atom volume dictionary as a look up table.
    atom_vol = {
        1:   7.24, #H
        6:  20.58, #C
        7:  15.60, #N
        8:  14.71, #O
        9:  13.31, #F
        17: 22.45, #Cl
        35: 26.52, #Br
        53: 32.52, #I
        15: 24.43, #P
        16: 24.43, #S
        33: 26.52, #As
        5:  40.48, #B
        14: 38.79, #Si
        34: 28.73, #Se
        52: 36.62  #Te
    }
    
    vol = 0

    #all atom contributions
    for atom in obmol.atoms:
        vol += atom_vol[atom.atomicnum];
        
    #5.92Nb
    vol -= obmol.OBMol.NumBonds()*5.92

    #14.7Ra, 3.8Rnr
    for ring in obmol.OBMol.GetLSSR():
        if ring.IsAromatic():
            vol -= 14.7;
        else:
            vol -= 3.8;

    return vol;
    


if __name__ == "__main__":
    mol = pybel.readstring("smi", "CC=C(N)C");
    print estimate_volume(mol);
