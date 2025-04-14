
import glob
import re
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np
import os.path
import pickle
import scipy
from statistics import mean, stdev
from math import sqrt, log10
from packaging.version import Version

project = "busybox"
output_directory = f'output-{project}'
figures_directory = f'src/public/figures'
default_height = 270

pio.templates['colorblind'] = go.layout.Template(layout_colorway=['#648FFF', '#FE6100', '#785EF0', '#DC267F', '#FFB000'])
pio.templates.default = 'plotly_white+colorblind'

def group_by_arch(df):
    grouped = df.groupby('architecture')
    dfs = {arch: group for arch, group in grouped}
    return dfs

def read_dataframe(stage, dtype={}, usecols=None, file=None, arch=None):
    if not file:
        file = 'output'
    df = pd.read_csv(f'{output_directory}/{stage}/{file}.csv', dtype=dtype, usecols=usecols)
    if 'committer_date_unix' in df:
        df['committer_date'] = df['committer_date_unix'].apply(lambda d: pd.to_datetime(d, unit='s'))
    if arch != None:
        return group_by_arch(df)[arch]
    return df

def replace_values(df):
    df.replace('kconfigreader', 'KConfigReader', inplace=True)
    df.replace('kmax', 'KClause', inplace=True)

def big_log10(str):
    return log10(int(str)) if not pd.isna(str) and str != '' else pd.NA

def process_model_count(df_solve):
    df_solve['model-count'] = df_solve['model-count'].replace('1', '')
    df_solve['model-count-log10'] = df_solve['model-count'].fillna('').apply(big_log10).replace(0, np.nan)
    df_solve['year'] = df_solve['committer_date'].apply(lambda d: int(d.year))

def peek_dataframe(df, column, message, type='str', filter=['revision', 'extractor']):
    success = df[~df[column].str.contains('NA') if type == 'str' else ~df[column].isna()][filter]
    failure = df[df[column].str.contains('NA') if type == 'str' else df[column].isna()][filter]
    print(f'{message}: {len(success)} successes, {len(failure)} failures')

def filter_system(df, ignore):
    return df[df["system"] not in ignore]

from plot_helpers import sloc, total_features, model_count, model_count_time
import json
def read_json(path):
    with open(path) as json_data:
        return json.load(json_data)

projects = read_json("gen_initJsonConfig.json")
for project, config in projects.items():
    df_kconfig = read_dataframe('kconfig' ignore=config["ignore_systems"])
    df_kconfig['year'] = df_kconfig['committer_date'].apply(lambda d: int(d.year))
    replace_values(df_kconfig)
    df = filter_system(df, config["ignore_systems"])
    sloc()
    total_features()
    model_count()
    model_count_time()
