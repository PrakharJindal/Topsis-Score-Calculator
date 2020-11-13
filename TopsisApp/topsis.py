# python topsis.py topsis_data.csv "1,1,1,2" "+,+,-,+" result.csv

import numpy as np
import pandas as pd


rssRow = []


def rss(val):
    s = 0
    for x in val:
        s += np.square(x)
    s = np.sqrt(s)
    rssRow.append(s)


ideal_best = []
ideal_worst = []


best_dist = []
worst_dist = []


def euclidean_distance(val):

    s_plus = 0
    s_minus = 0
    for x, y, z in zip(list(val), ideal_best, ideal_worst):
        s_plus += np.square(x-y)
        s_minus += np.square(x-z)
    s_plus = np.sqrt(s_plus)
    s_minus = np.sqrt(s_minus)
    best_dist.append(s_plus)
    worst_dist.append(s_minus)


def CalculateTopsisScore(file, weight, impact):
    outputName = ".".join(file.split(".")[:-1])

    df = pd.read_csv("/media/{}".format(file))
    df_original = pd.read_csv("/media/{}".format(file))

    if len(df.columns[1:]) != len(weight):
        return {"error": True, "msg": "No. Of weights on not equal to data size !"}

    elif len(df.columns[1:]) != len(impact):
        return {"error": True, "msg": "No. Of imapacts on not equal to data size !"}

    elif len(df.columns[1:]) < 3:
        return {"error": True, "msg": "Input File must have More than 3 columns !"}

    df.iloc[:, 1:].apply(func=rss, axis=0)

    for ind, val in enumerate(df.iloc[:, 1:].columns):
        df[val] = (df[val] / rssRow[ind]) * weight[ind]

    for ind, val in enumerate(df.iloc[:, 1:].columns):
        if impact[ind] == "+":
            ideal_best.append(df[val].max())
            ideal_worst.append(df[val].min())
        if impact[ind] == "-":
            ideal_best.append(df[val].min())
            ideal_worst.append(df[val].max())

    df.iloc[:, 1:].apply(func=euclidean_distance, axis=1)

    sum_dist = [x+y for x, y in zip(best_dist, worst_dist)]
    performance = [x/y for x, y in zip(worst_dist, sum_dist)]

    best_dist_df = pd.DataFrame(
        performance, columns=["Topsis Score"])

    df_original = pd.concat([df_original, best_dist_df], axis=1)

    df_original['Rank'] = df_original['Topsis Score'].rank(ascending=0)

    df_original.to_csv("/media/{}-Output.csv".format(outputName))

    return("/media/{}-Output.csv".format(outputName))
