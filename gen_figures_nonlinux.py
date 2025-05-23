import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np
from plot_helpers_nonlinux import sloc, total_features, model_count, model_count_time
import json
import argparse as ap
import os
from tqdm import tqdm
from metrics_helpers import *

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
        self.keymap = {
            "source_lines_of_code": "source_lines_of_code",
            "model-features": "total-features",
            "model-time": "model-count-time",
            "model-literals": "model-count"
        }
        self.metrics = {proj: dict() for proj in self.config.keys()}
        self.generate_figures()
        self.generate_metrics()

    def group_by_arch(self, df):
        grouped = df.groupby('architecture')
        dfs = {arch: group for arch, group in grouped}
        return dfs

    def read_dataframe(self, output_directory, stage, file=None):
        if not file:
            file = 'output'
        df = pd.read_csv(
            f'{output_directory}/{stage}/{file}.csv')
        if 'committer_date_unix' in df:
            df['committer_date'] = df['committer_date_unix'].apply(
                lambda d: pd.to_datetime(d, unit='s'))
        return df

    def filter_system(self, df, ignore):
        return df[~df["system"].isin(ignore)]

    def generate_figures(self):
        for project, config in (pbar := tqdm(self.config.items())):
            pbar.set_description(f"Processing {project}")
            figures_directory = "src/public/figures"
            figures_directory = config.get(
                "figures_directory", figures_directory)
            if not os.path.exists(figures_directory):
                os.mkdir(figures_directory)
            self.df = self.filter_system(self.read_dataframe(
                config["output_directory"], 'kconfig'), ignore=config["ignore_systems"])
            self.df['year'] = self.df['committer_date'].apply(
                lambda d: int(d.year))
            sloc(self.df, project, output_dir=figures_directory)
            total_features(self.df, project, output_dir=figures_directory)
            model_count(self.df, project, output_dir=figures_directory)
            model_count_time(self.df, project, output_dir=figures_directory)

    def try_history(self, last_date, key, unit, prefix, last_value, apply_func=None, ):
        history = [1, 2, 5, 10]
        curyear = last_date.iloc[0]
        if self.keymap[key] not in self.metrics[self.current_project]:
            self.metrics[self.current_project][self.keymap[key]] = {}
        self.metrics[self.current_project][self.keymap[key]]["history"] = dict()
        history_vals = {"history": dict()}
        for last in history:
            ym = curyear - pd.Timedelta(last*365, "d")
            value = self.df[self.df["committer_date_readable"].str.contains(
                ym.strftime("%Y-%m"))].tail(1)
            if value.empty:
                ym = ym - pd.Timedelta(30, "d")
                value = self.df[self.df["committer_date_readable"].str.contains(
                    ym.strftime("%Y-%m"))].tail(1)
            if value.empty:
                ym = ym + pd.Timedelta(30, "d")
                value = self.df[self.df["committer_date_readable"].str.contains(
                    ym.strftime("%Y-%m"))].tail(1)
            if value.empty:
                value = self.df[self.df["committer_date_readable"].str.contains(
                    ym.strftime("%Y"))].tail(1)
            if value.empty:
                continue
            value = value.iloc[0][key]
            if apply_func and not np.isnan(value):
                last_value = apply_func(last_value)
                value = apply_func(value)
            else:
                continue

            history_vals["history"][f"{last}-years-before"] = {
                "value": f"{prefix}{value} {unit}",
                "date": ym.strftime("%B %d, %Y")
            }
        return history_vals

    def get_latest_nonLinux(self, key, unit, prefix, apply_func=None):
        date_prefix = ""
        value = self.df.sort_values(
            by="committer_date_unix").dropna(subset=[key]).tail(1)
        history = {"history": dict()}
        if not value.empty:
            date = pd.to_datetime(value["committer_date_readable"])
            history = self.try_history(last_date=date, key=key, unit=unit,
                                    prefix=prefix, apply_func=apply_func, last_value=value.iloc[0][key])
            date = date.dt.strftime("%B %d, %Y").iloc[0]
            date_prefix = "From"
            value = value.iloc[0][key]
            if apply_func and not np.isnan(value):
                value = apply_func(value)
                self.metrics[self.current_project][self.keymap[key]] = {
                    "currentValue": {
                        "value": f"{prefix}{value} {unit}",
                        "date": f"{date_prefix} {date}"
                    },
                    "history": history["history"]
                }

    def generate_metrics(self):
        for project, config in (pbar := tqdm(self.config.items())):
            pbar.set_description(f"Processing {project}")
            print(f"Generating metrics for '{project}'")
            self.current_project = project
            ignore_systems = config["ignore_systems"]
            output_directory = config["output_directory"]
            self.df = self.filter_system(self.read_dataframe(
                output_directory, 'kconfig'), ignore=ignore_systems)
            self.get_latest_nonLinux(
                key="source_lines_of_code", unit="loc", prefix="", apply_func=lambda v: int(v))
            self.get_latest_nonLinux(
                key="model-features", unit="features", prefix="", apply_func=lambda v: int(v))
            self.get_latest_nonLinux(
                key="model-time", unit="s", prefix="", apply_func=lambda v: round(v / 1000000000, 3))
            self.get_latest_nonLinux(
                key="model-literals", unit="models", prefix="", apply_func=lambda v: int(v))
        merge_metrics(self.metrics)


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
