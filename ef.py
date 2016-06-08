# coding: UTF-8 

import pandas as pd

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


    df = pd.DataFrame.from_dict({"value": values, "label": labels})
    df = df.sort_values("value", ascending=False).reset_index();
    del df["index"]
    
    df.label = df.label.astype(float)

    all_ratio = sum(df.label) / len(df)
    index = int(len(df)*ratio)
    partial_df = df[:index]

    meaned_label = df[df.value == df.loc[index-1].value].label.mean()
    df.loc[df.value == df.loc[index-1].value, "label"] = meaned_label

    partial_df = df[:int(len(df)*ratio)] # refresh
    par_ratio = sum(partial_df.label) / len(partial_df)
    ef = par_ratio / all_ratio;
    print ef
    return ef

def test(cond, statement_dict):
    if cond:
        print("A test is passed.")
        for key, value in statement_dict.iteritems():
            print(key, value)

if __name__ == '__main__':
    values = [1, 2, 3, 4, 5]
    labels = [0, 0, 1, 0, 1]
    
    case1 = {
        "values": values,
        "labels": labels,
        "ratio" : 0.2,
        "result": 2.5
    }

    test(ef(case1["values"], case1["labels"], case1["ratio"]) == case1["result"], case1)


    case2 = case1
    case2["definition"] = (1,0)
    case2["result"] = 0
    test(ef(case2["values"], case2["labels"], case2["ratio"], definition=case2["definition"]) == case2["result"], case2)
