# -*- coding: utf-8 -*-
import configparser
import os


def read_config(filepath):
    """
    Configファイルを読み込む。

    Parameters
    --------
    filepath : str
        Configファイルのパス。

    Returns
    --------
    dat : configparser.ConfigParser
        Configファイルを読み込んだ結果のオブジェクト。

    Raises
    --------
    FileNotFoundError
        filepath にファイルが存在しない場合に発生。
    """

    dat = configparser.ConfigParser()
    with open(filepath) as fin:
        dat.read_file(fin)
    return dat


def TEST_read_config():
    os.system("touch .test.conf")
    dat = read_config(".test.conf")
    assert(type(dat) == configparser.ConfigParser)

    os.system("touch .notexist.conf; rm .notexist.conf")
    try:
        dat2 = read_config(".notexist.conf")
    except FileNotFoundError:
        None
    else:
        assert(False)  # FileNotFoundError should be happened


if __name__ == "__main__":
    TEST_read_config()
