import pandas as pd
import numpy as np
import os
import json
import pickle
from math import log10


# METRIC GENERATION UTILITY FUNCTIONS


def replace_values(df):
    df.replace("kconfigreader", "KConfigReader", inplace=True)
    df.replace("kmax", "KClause", inplace=True)


def big_log10(str):
    return log10(int(str)) if not pd.isna(str) and str != "" else pd.NA


def process_model_count(df_solve):
    df_solve["model-count"] = df_solve["model-count"].replace("1", "")
    df_solve["model-count-log10"] = (
        df_solve["model-count"].fillna("").apply(big_log10).replace(0, np.nan)
    )
    df_solve["year"] = df_solve["committer_date"].apply(lambda d: int(d.year))


def unify_solvers(df, columns=['model-count-unconstrained-log10']):
    return df[['revision', 'committer_date', 'architecture', 'extractor', *columns]].drop_duplicates()


def big_sum(series):
    big_sum = sum([int(value)
                  for value in series if not pd.isna(value) and value])
    if big_sum > 0:
        return len(str(big_sum))


def write_object_to_file(obj, name):
    with open(name, "w") as fp:
        json.dump(obj, fp)


def read_json(path):
    with open(path) as json_data:
        return json.load(json_data)


LINUX_PLOTCONFIG = {
    "configuration-evolution-arch": {
        "plotType": "box",
        "allOnly": False
    },
    "configuration-evolution-total": {
        "plotType": "box",
        "allOnly": True
    },
    "configuration-similarity": {
        "plotType": "box",
        "allOnly": False
    },
    "feature-evolution-arch": {
        "plotType": "box",
        "allOnly": False
    },
    "feature-evolution-total": {
        "plotType": "box",
        "allOnly": True
    },
    "features": {
        "plotType": "scatter",
        "allOnly": False
    },
    "jaccard-similarity": {
        "plotType": "box",
        "allOnly": False
    },
    "model-count": {
        "plotType": "scatter",
        "allOnly": False
    },
    "model-count-time": {
        "plotType": "scatter",
        "allOnly": False
    },
    "prediction-accuracy-configurations": {
        "plotType": "box",
        "allOnly": False
    },
    "prediction-accuracy-configurations-by-features": {
        "plotType": "box",
        "allOnly": False
    },
    "prediction-accuracy-features": {
        "plotType": "box",
        "allOnly": False
    },
    "share-of-feature-variables": {
        "plotType": "box",
        "allOnly": False
    },
    "source_lines_of_code": {
        "plotType": "scatter",
        "allOnly": False
    },
    "total-features": {
        "plotType": "scatter",
        "allOnly": True
    }
}


def merge_metrics(new, init_json_path="src/public/init.json"):
    old = read_json(init_json_path)
    if "projectData" not in old:
        old["projectData"] = dict()
    for proj, metrics in new.items():
        for metric, values in metrics.items():
            for name, value in values.items():
                if proj not in old["projectData"]:
                    if "linux" in proj:
                        old["projectData"][proj] = {plot: dict() for plot, val in LINUX_PLOTCONFIG.items(
                        ) if val["plotType"] == "box" and val["allOnly"] == (proj == "linux/all")}
                    else:
                        old["projectData"][proj] = dict()
                if metric not in old["projectData"][proj]:
                    if proj == "linux/all" and LINUX_PLOTCONFIG[metric]["allOnly"]:
                        old["projectData"][proj][metric] = dict()
                    elif proj != "linux/all" and "linux" in proj and not LINUX_PLOTCONFIG[metric]["allOnly"]:
                        old["projectData"][proj][metric] = dict()
                    else:
                        old["projectData"][proj][metric] = dict()
                if metric in old["projectData"][proj]:
                    old["projectData"][proj][metric][name] = value
    write_object_to_file(old, init_json_path)
