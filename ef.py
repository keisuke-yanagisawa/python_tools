# coding: UTF-8 

import pandas as pd
import numpy as np

def ef(values, labels, ratio, definition=(0,1)):
    """
    INPUT
    values     : value list for sorting (descending order is assumed)
    labels     : label list for evaluation
    ratio      : a ratio of EF that you want to calculate
    definition : definition of positive and negative labels (default=(0,1), 0 for neg, 1 for pos)

    OUTPUT
    an enrichment factor (ratio)
    """

    if len([x for x in labels if (not x in definition)]) != 0:
        print("invalid labels are detected.")
        print([x for x in labels if (not x in definition)])
        return None
    labels = [definition.index(x) for x in labels]

    ratio1 = np.sum(labels, dtype=float)/len(labels)

    df = pd.DataFrame.from_dict({"value": values, "label": labels})
    df = df.sort_values("value", ascending=False).reset_index();
    del df["index"]

    meaned_label_df = df.groupby("value").mean().reset_index();
    df = pd.merge(df[["value"]], meaned_label_df, on="value", how="left")

    index = int(len(labels)*ratio)
    partial_df = df[:index]
    par_ratio = float(sum(partial_df.label)) / index
    ef = par_ratio / ratio1;
    print ef
    return ef

def test(cond, statement_dict):
    if cond:
        print("A test is passed.")
    else:
        print("A test is failed.")
    for key, value in statement_dict.iteritems():
        print(key, value)

if __name__ == '__main__':
    case1 = {
        "values": [1, 2, 3, 4, 5],
        "labels": [0, 0, 1, 0, 1],
        "ratio" : 0.2,
        "result": 2.5,
    }
    test(ef(case1["values"], case1["labels"], case1["ratio"]) == case1["result"], case1)


    case2 = case1
    case2["definition"] = (1,0)
    case2["result"] = 0
    test(ef(case2["values"], case2["labels"], case2["ratio"], definition=case2["definition"]) == case2["result"], case2)

    #TODO the result of case3 is wrong.
    case3 = case2
    case3["values"] = [1,2,4,5,5]
    case3["ratio"] = 0.4
    case3["result"] = (1.0/2) / (2.0/5)
    test(ef(case3["values"], case3["labels"], case3["ratio"], definition=case3["definition"]) == case3["result"], case3)
