# -*- coding: utf-8 -*-

from subprocess import getoutput as gop
import os.path
import gzip


def __isCompressed(filepath):
    """
    拡張子を元にファイルがgzip形式で圧縮されているかどうかを判定する。

    Parameters
    --------
    filepath : str
        対象のファイル名。

    Returns
    --------
    is_gzip : bool
        gzip形式か否か。
    """

    _, ext = os.path.splitext(filepath)
    is_gzip = ext == ".gz"
    return is_gzip


def size(filepath):
    """
    SDFファイル内に存在する化合物数をカウントする。

    Parameters
    --------
    filepath : str
        対象のSDFファイル名。

    Returns
    --------
    count : int
        化合物数。

    Notes
    --------
    `grep`, `gzip`, `cat`を利用してカウントする。
    """

    command = "grep \$\$\$\$ | wc -l"
    if(__isCompressed(filepath)):
        file_read = "gzip -cd %s" % filepath
    else:
        file_read = "cat %s" % filepath

    count = int(gop(file_read+" | "+command))
    return count


def cpdsGenerator(filepath):
    """
    yielding a compound data string.
    """
    if(__isCompressed(filepath)):
        File = gzip.open(filepath)
    else:
        File = open(filepath)

    string = ""
    for line in File:
        string += line
        if(line.startswith("$$$$")):
            yield string
            string = ""
    File.close()


def getCpds(filepath, indices=None):
    """
    Getting compound string list, based on given indices list 
    Indices list is uniqued list, which has 0-origin indices.
    If indices is None, all compounds will listed.
    """

    if(indices is None):
        return list(cpdsGenerator(sys.argv[1]))

    # else:
    gen = cpdsGenerator(filepath)
    ret = []
    indices = sorted(indices)
    count = 0
    for index in indices:
        while(count < index):
            next(gen)
            count += 1
        ret.append(next(gen))
        count += 1
    gen.close()
    return ret


if __name__ == "__main__":
    import sys
    print(size(sys.argv[1]))
    print(len(list(cpdsGenerator(sys.argv[1]))))
    print(getCpds(sys.argv[1], indices=[3]))
