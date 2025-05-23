import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np
from plot_helpers_nonlinux import sloc, total_features, model_count, model_count_time
import json
from math import log10
import argparse as ap
import os
from tqdm import tqdm

# NONCONFIGURABLE VARIABLES
init_json_path = "src/public/init.json"  # exact path needed for frontend
pio.templates['colorblind'] = go.layout.Template(
    layout_colorway=['#648FFF', '#FE6100', '#785EF0', '#DC267F', '#FFB000'])
pio.templates.default = 'plotly_white+colorblind'


def read_json(path):
    with open(path) as json_data:
        return json.load(json_data)


class NonLinux:
    def __init__(self, config):
        self.config = read_json(config).get("nonLinux", dict())
        self.generate_figures()

    def group_by_arch(self, df):
        grouped = df.groupby('architecture')
        dfs = {arch: group for arch, group in grouped}
        return dfs

    def read_dataframe(self, output_directory, stage, dtype={}, usecols=None, file=None, arch=None):
        if not file:
            file = 'output'
        df = pd.read_csv(
            f'{output_directory}/{stage}/{file}.csv', dtype=dtype, usecols=usecols)
        if 'committer_date_unix' in df:
            df['committer_date'] = df['committer_date_unix'].apply(
                lambda d: pd.to_datetime(d, unit='s'))
        if arch is not None:
            return self.group_by_arch(df)[arch]
        return df

    def filter_system(self, df, ignore):
        return df[~df["system"].isin(ignore)]

    def generate_figures(self):
        for project, config in (pbar := tqdm(self.config.items())):
            pbar.set_description(f"Processing {project}")
            figures_directory = "src/public/figures"
            figures_directory = config.get(
                "figures_directory", figures_directory)
            # print(f"Will save figures for '{project}' to {figures_directory}")
            if not os.path.exists(figures_directory):
                os.mkdir(figures_directory)
            df = self.filter_system(self.read_dataframe(
                config["output_directory"], 'kconfig'), ignore=config["ignore_systems"])
            df['year'] = df['committer_date'].apply(lambda d: int(d.year))
            sloc(df, project, output_dir=figures_directory)
            total_features(df, project, output_dir=figures_directory)
            model_count(df, project, output_dir=figures_directory)
            model_count_time(df, project, output_dir=figures_directory)


def nonlinux_main(config: str):
    NonLinux(config)


if __name__ == '__main__':
    # CONFIGURABLE VARIABLES
    parser = ap.ArgumentParser("NonLinux Figure Generator")
    parser.add_argument("--config", "-c", type=str, required=True)
    args = parser.parse_args()
    config = args.config if os.path.exists(args.config) else None
    if config:
        nonlinux_main(config)
