import pybel
import matplotlib.pyplot as plt

def hist(data, bins, xlabel="x", ylabel="y", pngfile=None):
    plt.hist(data, bins=bins)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if(pngfile==None):
        plt.show()
    else:
        plt.savefig(pngfile)

def molwtHist(sdffile, bins=10, pngfile=None):
    data=[]
    for mol in pybel.readfile("sdf", sdffile):
        data.append(mol.molwt)

    hist(data, bins,
         xlabel="molecular weight",
         ylabel="frequency",
         pngfile=pngfile)

if __name__ == "__main__":
    import sys
    molwtHist(sys.argv[1], range(0,800,50), pngfile="hoge.png")
