import pandas as pd
import numpy as np
import os
import json
import pickle
from math import log10
from plot_helpers_linux import *
from metrics_helpers import *
from tqdm import tqdm
from argparse import ArgumentParser
# UTILITY FUNCTIONS


def read_dataframe(
    stage, dtype={}, usecols=None, file=None, output_directory="output-linux"
):
    if not file:
        file = "output"
    df = pd.read_csv(
        f"{output_directory}/{stage}/{file}.csv", dtype=dtype, usecols=usecols
    )
    if "committer_date_unix" in df:
        df["committer_date"] = df["committer_date_unix"].apply(
            lambda d: pd.to_datetime(d, unit="s")
        )
    return df


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


class Linux:
    def __init__(self, config: str):
        self.config = read_json(config)
        self.output_directory = self.config["linux"].get(
            "output_directory", "output-linux")
        if not os.path.exists(self.output_directory):
            print(
                f"Specifed TORTE experiment output directory for linux under '{self.output_directory} does not exist. aborting.")
            return
        print(f"Reading Linux Dataframes from {self.output_directory}")
        self.figures_directory = "src/public/figures"
        self.figures_directory = self.config["linux"].get(
            "figures_directory", self.figures_directory)
        self.figures_directory = self.config.get(
            "figures_directory", self.figures_directory)
        print(f"Will save figures to {self.figures_directory}")
        if not os.path.exists(self.figures_directory):
            os.mkdir(self.figures_directory)
        self.df_kconfig = self.read_dataframe("kconfig")
        self.df_kconfig["year"] = self.df_kconfig["committer_date"].apply(
            lambda d: int(d.year)
        )
        self.df_architectures = self.read_dataframe("read-linux-architectures")
        self.architectures = self.df_architectures["architecture"].unique()
        self.architectures = np.append(self.architectures, "all")
        self.df_architectures = self.df_architectures.sort_values(
            by="committer_date")
        self.df_architectures["year"] = self.df_architectures["committer_date"].apply(
            lambda d: int(d.year)
        )
        self.df_configs = self.read_dataframe("read-linux-configs")
        self.df_configs = self.df_configs[
            ~self.df_configs["kconfig-file"].str.contains("/um/")
        ]
        self.df_config_types = self.read_dataframe(
            "read-linux-configs", file="output.types"
        )
        self.df_config_types = self.df_config_types[
            ~self.df_config_types["kconfig-file"].str.contains("/um/")
        ]
        self.df_config_types = self.df_config_types.merge(
            self.df_architectures[["revision",
                                   "committer_date"]].drop_duplicates()
        )
        self.df_uvl = self.read_dataframe("model_to_uvl_featureide")
        self.df_smt = self.read_dataframe("model_to_smt_z3")
        self.df_dimacs = self.read_dataframe("dimacs")
        self.df_backbone_dimacs = self.read_dataframe("backbone-dimacs")
        self.df_solve = self.read_dataframe(
            "solve_model-count", {"model-count": "string"}
        )
        process_model_count(self.df_solve)
        if os.path.isfile(f'{self.output_directory}/model-count-with-6h-timeout.csv'):
            self.df_solve_6h = pd.read_csv(
                f'{self.output_directory}/model-count-with-6h-timeout.csv', dtype={'model-count': 'string'})
            self.df_solve_6h = self.df_backbone_dimacs.merge(self.df_solve_6h)
            process_model_count(self.df_solve_6h)
            self.df_solve = pd.merge(self.df_solve, self.df_solve_6h[['revision', 'architecture', 'extractor', 'backbone.dimacs-analyzer']], indicator=True, how='outer') \
                .query('_merge=="left_only"') \
                .drop('_merge', axis=1)
            self.df_solve = pd.concat([self.df_solve, self.df_solve_6h])
        else:
            self.df_solve_6h = None
        for df in [
            self.df_kconfig,
            self.df_uvl,
            self.df_smt,
            self.df_dimacs,
            self.df_backbone_dimacs,
            self.df_solve,
        ]:
            df.replace("kconfigreader", "KConfigReader", inplace=True)
            df.replace("kmax", "KClause", inplace=True)
        self.df_configs_configurable = self.df_configs.copy()
        self.df_configs_configurable["configurable"] = False
        with open(f"{self.output_directory}/linux-features.dat", "rb") as f:
            [
                self.features_by_kind_per_architecture,
                self.df_extractor_comparison,
                self.potential_misses_grep,
                self.potential_misses_kmax,
                self.df_configs_configurable,
            ] = pickle.load(f)

        replace_values(self.features_by_kind_per_architecture)
        self.df_features = pd.merge(
            self.df_architectures, self.features_by_kind_per_architecture, how="outer"
        ).sort_values(by="committer_date")
        self.df_features = pd.merge(
            self.df_kconfig, self.df_features, how="outer"
        ).sort_values(by="committer_date")
        self.df_total_features = (
            self.df_features.groupby(["extractor", "revision"])
            .agg({"#total_features": "min"})
            .reset_index()
        )
        self.df_total_features = pd.merge(
            self.df_kconfig[["committer_date", "revision"]].drop_duplicates(),
            self.df_total_features,
        )
        self.df_solve_unconstrained = self.df_solve.merge(self.df_features)
        self.df_solve_unconstrained["model-count-unconstrained"] = self.df_solve_unconstrained.apply(
            lambda row: str(
                int(row["model-count"])
                * (2 ** int(row["unconstrained_bools"]))
                * (3 ** int(row["unconstrained_tristates"]))
            )
            if not pd.isna(row["model-count"]) and row["model-count"] != ""
            else pd.NA,
            axis=1,
        )
        self.df_solve_unconstrained["model-count-unconstrained-log10"] = (
            self.df_solve_unconstrained["model-count-unconstrained"]
            .fillna("")
            .map(big_log10)
            .replace(0, np.nan)
        )
        self.df_solve_unconstrained["similarity"] = self.df_solve_unconstrained.apply(
            lambda row: int(row["model-count"]) /
            int(row["model-count-unconstrained"])
            if not pd.isna(row["model-count"]) and row["model-count"] != ""
            else pd.NA,
            axis=1,
        )

        print("About halfway done..")

        def unify_solvers(df, columns=['model-count-unconstrained-log10']):
            return df[['revision', 'committer_date', 'architecture', 'extractor', *columns]].drop_duplicates()

        def big_sum(series):
            big_sum = sum([int(value)
                          for value in series if not pd.isna(value) and value])
            if big_sum > 0:
                return len(str(big_sum))

        def evaluate_metric(df, extractor, x_value, x, y):
            rows = df[(df['extractor'] == extractor) & (
                df[x] >= x_value)].sort_values(by=x)
            if len(rows) > 0:
                return rows[rows[x] == rows.iloc[0][x]][y].median()

        def estimate_metric(df, x, y, extractor, key=lambda x: x.timestamp()):
            df_all = df[(df['extractor'] == extractor)].sort_values(
                by=x).dropna(subset=[y])
            if len(df_all) < 3:
                return []
            df_all['kind'] = 'actual'
            mid = len(df_all) * -1 // 2 * -1
            df_train = df_all[0:mid]
            df_test = df_all[mid:]
            fig = px.scatter(
                df_train,
                x=x,
                y=y,
                trendline='ols'
            )
            xs = list(df_test[x])
            a = estimate_trend(fig, xs=xs, key=key)
            estimated_values = a[4]
            deviations = []
            for (x_value, estimated_value) in zip(xs, estimated_values):
                actual_value = evaluate_metric(df, extractor, x_value, x, y)
                deviation = estimated_value / actual_value - 1
                deviations.append(deviation)
            return deviations

        self.df_solve_slice = self.df_solve_unconstrained[self.df_solve_unconstrained['year'] <= 2013]
        self.df_solve_failures = self.df_solve_slice.groupby(['extractor', 'revision', 'architecture'], dropna=False).agg(
            {'model-count-unconstrained-log10': lambda x: (True in list(pd.notna(x)) or pd.NA)}).reset_index()
        self.df_solve_group = self.df_solve_failures.groupby(
            ['extractor', 'revision'], dropna=False)
        self.df_solve_failures = (self.df_solve_group['model-count-unconstrained-log10'].size(
        ) - self.df_solve_group['model-count-unconstrained-log10'].count()).reset_index()
        self.df_solve_failures['is-upper-bound'] = self.df_solve_failures['model-count-unconstrained-log10'] == 0
        self.df_solve_failures = self.df_solve_failures.rename(
            columns={'model-count-unconstrained-log10': 'failures'})
        self.df_solve_total = unify_solvers(pd.merge(self.df_solve_slice, self.df_solve_failures), [
                                            'model-count-unconstrained', 'model-count-unconstrained-log10', 'is-upper-bound', 'failures', 'year'])
        self.df_solve_total = self.df_solve_total.groupby(['extractor', 'committer_date', 'year']).agg(
            {'model-count-unconstrained': big_sum, 'is-upper-bound': 'min', 'failures': 'min'}).reset_index()

        self.df_features_and_configurations = pd.merge(
            self.df_features, unify_solvers(self.df_solve_unconstrained))
        self.df_features_and_configurations = self.df_features_and_configurations[
            ~self.df_features_and_configurations['model-count-unconstrained-log10'].isna()]
        self.df_features_and_configurations_total = pd.merge(self.df_features.drop(
            columns=['#features']).drop_duplicates(), self.df_solve_total)
        self.df_features_and_configurations_total = self.df_features_and_configurations_total[~self.df_features_and_configurations_total[
            'model-count-unconstrained'].isna() & self.df_features_and_configurations_total['is-upper-bound']]
        self.df_features_and_configurations_total.rename(
            columns={'#total_features': '#features', 'model-count-unconstrained': 'model-count-unconstrained-log10'}, inplace=True)
        self.df_features_and_configurations_total['architecture'] = 'TOTAL'
        self.df_features_and_configurations_total = self.df_features_and_configurations_total[[
            '#features', 'model-count-unconstrained-log10', 'extractor', 'revision', 'architecture']].drop_duplicates().dropna()
        self.df_features_and_configurations_scatter = self.df_features_and_configurations[[
            '#features', 'model-count-unconstrained-log10', 'extractor', 'revision', 'architecture']]
        self.df_features_and_configurations_scatter = pd.concat(
            [self.df_features_and_configurations_scatter, self.df_features_and_configurations_total])

        self.df_solve_total_exact = self.df_solve_total.copy().sort_values(by='committer_date')
        self.df_solve_total_exact = self.df_solve_total_exact[
            self.df_solve_total_exact['is-upper-bound']]
        self.df_solve_unconstrained_unified = unify_solvers(
            self.df_solve_unconstrained).copy().sort_values(by='committer_date')

        deviations = []
        for extractor in ['KConfigReader', 'KClause']:
            for (df, metric, x, column, arch, key) in \
                [(self.df_total_features, 'features', 'committer_date', '#total_features', 'TOTAL', None)] + \
                [(self.df_features[self.df_features['architecture'] == arch], 'features', 'committer_date', '#features', arch, None) for arch in set(self.df_features['architecture'].drop_duplicates())] + \
                [(self.df_solve_total_exact, 'configurations', 'committer_date', 'model-count-unconstrained', 'TOTAL', None)] + \
                [(self.df_solve_unconstrained_unified[self.df_solve_unconstrained_unified['architecture'] == arch], 'configurations', 'committer_date', 'model-count-unconstrained-log10', arch, None) for arch in set(self.df_solve_unconstrained_unified['architecture'].drop_duplicates())] + \
                [(self.df_features_and_configurations_total, 'configurations-by-features', '#features', 'model-count-unconstrained-log10', 'TOTAL', lambda x: x)] + \
                    [(self.df_features_and_configurations[self.df_features_and_configurations['architecture'] == arch], 'configurations-by-features', '#features', 'model-count-unconstrained-log10', arch, lambda x: x) for arch in set(self.df_features_and_configurations['architecture'].drop_duplicates())]:
                current_deviations = estimate_metric(
                    df, x, column, extractor, key if key is not None else lambda x: x.timestamp())
                deviations.extend([{'extractor': extractor, 'architecture': arch, 'deviation': deviation,
                                  'is-total': arch == 'TOTAL', 'metric': metric} for deviation in current_deviations])
        self.deviations = pd.DataFrame(deviations)
        self.deviations.replace(
            {'extractor': {'KConfigReader': 'KCR', 'KClause': 'KCl'}}, inplace=True)
        self.deviations.replace(
            {'is-total': {True: 'Total', False: 'Per Arch.'}}, inplace=True)

        self.keymap = {
            "#total_features": "total-features",
            "#features": "features",
            "backbone.dimacs-analyzer-time": "model-count-time",
            "model-count-unconstrained-log10": "model-count",
            "model-count-unconstrained": "model-count",
            "source_lines_of_code": "source_lines_of_code"
        }
        self.metrics = {f"linux/{arch}": dict()
                        for arch in self.df_kconfig["architecture"].unique()}
        self.metrics["linux/all"] = dict()
        # self.generate_figures()
        self.generate_metrics()

    def read_dataframe(self, stage, dtype={}, usecols=None, file=None):
        if not file:
            file = "output"
        df = pd.read_csv(
            f"{self.output_directory}/{stage}/{file}.csv", dtype=dtype, usecols=usecols
        )
        if "committer_date_unix" in df:
            df["committer_date"] = df["committer_date_unix"].apply(
                lambda d: pd.to_datetime(d, unit="s")
            )
        return df

    def solver_successes(self, solver):
        df_solve_for_solver = self.df_solve_attempts[~self.df_solve_attempts['model-count'].isna()]
        df_solve_for_solver = df_solve_for_solver[df_solve_for_solver['backbone.dimacs-analyzer'] == solver]
        return set(df_solve_for_solver['extractor'] + ',' + df_solve_for_solver['revision'] + ',' + df_solve_for_solver['architecture'])

    def filter_for_architecture(self, df, arch):
        return df[df["architecture"] == arch]

    def differentiate_extractors(self, arch, df, sortBy, key, prefix, unit, apply_func=None):
        """returns: {
            "extractor1": {
                "value": "<prefix><value1> <unit>",
                "date": "From <date1>"},
            "extractor2": {
                "value": "<prefix><value2> <unit>",
                "date": "From <date2>"
            }
        """
        vals = {"currentValue": dict()}
        for extractor in df["extractor"].unique():
            history = {"history": dict()}
            df_ex = df[df["extractor"] == extractor]
            if df_ex.empty:
                print(key, df["extractor"].unique(), extractor)
            ex_value = df_ex.dropna().sort_values(sortBy).last_valid_index()
            if ex_value not in df_ex.index:
                vals["currentValue"][extractor] = {
                    "currentValue": {
                        "value": f"0 {unit}",
                        "date": f"Date not Found"
                    },
                    "history": history["history"]
                }
                continue
            ex_value = df_ex.loc[ex_value]
            date = "Date not Found"
            date_prefix = ""
            if not ex_value.empty:
                date = ex_value["committer_date"]
                history = self.try_history(
                    arch=arch,
                    df=df_ex,
                    last_date=date,
                    key=key,
                    unit=unit,
                    prefix=prefix,
                    apply_func=apply_func,
                    last_value=ex_value[key],
                    date_func=lambda ym: df_ex["committer_date"].dt.strftime(
                        "%Y") == ym.strftime("%Y")
                )
                date = date.strftime("%B %d, %Y")
                date_prefix = "From"
                if apply_func:
                    ex_value = apply_func(ex_value[key])
            else:
                ex_value = 0
                prefix = ""

            vals["currentValue"][extractor] = {
                "currentValue": {
                    "value": f"{prefix}{ex_value} {unit}",
                    "date": f"{date_prefix} {date}"
                },
                "history": history
            }
        return vals

    def model_count_time_latest(self):
        archs = list(self.df_kconfig["architecture"].unique())
        for arch in archs:
            df_arch = self.df_solve_slice[self.df_solve_slice["architecture"] == arch]
            key = "backbone.dimacs-analyzer-time"
            extractor_values = self.differentiate_extractors(
                arch=arch, df=df_arch, sortBy="committer_date_unix", key=key, prefix="10^", unit="s", apply_func=lambda v: int(v)//1000000000)
            self.metrics[f"linux/{arch}"]["model-count-time"] = extractor_values

    def model_count_latest(self):
        archs = list(self.df_kconfig["architecture"].unique())
        archs.append("all")
        for arch in archs:
            df_arch = self.df_solve_slice[self.df_solve_slice["architecture"] == arch]
            key = "model-count-unconstrained-log10"
            sortBy = "committer_date_unix"
            if arch == 'all':
                df_arch = self.df_solve_total
                key = "model-count-unconstrained"
                sortBy = "committer_date"
            extractor_values = self.differentiate_extractors(
                arch=arch, df=df_arch, sortBy=sortBy, key=key, prefix="10^", unit="models", apply_func=lambda v: int(v))
            self.metrics[f"linux/{arch}"]["model-count"] = extractor_values

    def generate_metrics(self):
        print(f"Generating linux metrics & merging into src/public/init.json")
        self.total_features_latest()
        self.features_latest()
        self.sloc_latest()
        self.model_count_latest()
        self.model_count_time_latest()
        print(self.metrics)
        merge_metrics(self.metrics)

    def total_features_latest(self):
        extractor_values = self.differentiate_extractors(
            arch="all", df=self.df_total_features, sortBy="committer_date", key="#total_features", prefix="", unit="features", apply_func=lambda v: int(v))
        self.metrics["linux/all"]["total-features"] = extractor_values

    def features_latest(self):
        archs = list(self.df_kconfig["architecture"].unique())
        for architecture in archs:
            df = self.filter_for_architecture(self.df_features, architecture)
            extractor_values = self.differentiate_extractors(
                arch=architecture, df=df, sortBy="committer_date", key="#features", prefix="", unit="features", apply_func=lambda v: int(v))
            self.metrics[f"linux/{architecture}"]["features"] = extractor_values

    def sloc_latest(self):
        archs = list(self.df_kconfig["architecture"].unique())
        archs.append("all")
        key = "source_lines_of_code"
        for arch in archs:
            history = {"history": dict()}
            date = "Date not Found"
            date_prefix = ""
            df_arch = self.filter_for_architecture(self.df_kconfig, arch)
            if arch == "all":
                df_arch = self.df_kconfig
            value = df_arch.sort_values(by="committer_date_unix").tail(1)
            if not value.empty:
                date = pd.to_datetime(value["committer_date_readable"]).iloc[0]
                history = self.try_history(
                    arch=arch,
                    df=df_arch,
                    last_date=date,
                    key=key,
                    unit="loc",
                    prefix="",
                    apply_func=lambda x: int(x),
                    last_value=value.iloc[0][key],
                    date_func=lambda ym: df_arch["committer_date_readable"].str.contains(
                        ym.strftime("%Y-%m"))
                )
                date = date.strftime("%B %d, %Y")
                date_prefix = "From"
                value = int(value.iloc[0][key])
            else:
                value = 0
            self.metrics[f"linux/{arch}"][key] = {
                "currentValue": {
                    "value": f"{value} loc",
                    "date": f"{date_prefix} {date}"
                },
                "history": history
            }

    def try_history(self, arch, df, last_date, key, unit, prefix, last_value, date_func, apply_func=None, ):
        history = [1, 2, 5, 10]
        if key not in self.metrics[f"linux/{arch}"]:
            self.metrics[f"linux/{arch}"][self.keymap[key]] = {}
        self.metrics[f"linux/{arch}"][self.keymap[key]]["history"] = dict()
        history_vals = dict()
        for last in history:
            ym = last_date - pd.Timedelta(last*365, "d")
            value = df[date_func(ym)].tail(1)
            if value.empty:
                ym = ym - pd.Timedelta(30, "d")
                value = df[date_func(ym)].tail(1)
            if value.empty:
                ym = ym + pd.Timedelta(30, "d")
                value = df[date_func(ym)].tail(1)
            if value.empty:
                value = df[date_func(ym)].tail(1)
            if value.empty:
                continue
            value = value.iloc[0].replace(pd.NA, np.nan)[key]
            if np.isnan(value):
                continue
            if apply_func:
                last_value = apply_func(last_value)
                value = apply_func(value)
            if value != 0:
                history_vals[f"{last}-years-before"] = {
                    "value": f"{prefix}{value} {unit}",
                    "date": ym.strftime("%B %d, %Y")
                }
        return history_vals

    def generate_figures(self):
        print(f"Generating linux plots & Saving to {self.figures_directory}")
        for arch in (pbar := tqdm(self.architectures)):
            pbar.set_description(f"Processing {arch}")
            configuration_evolution(
                self.df_solve_total, self.df_solve_unconstrained_unified, arch, self.figures_directory)
            configuration_similarity(
                self.df_solve_unconstrained, arch, self.figures_directory)
            feature_evolution(self.df_features, arch, self.figures_directory)
            if arch != "all":
                features(self.df_features, arch, self.figures_directory)
            jaccard_similarity(self.df_features, arch, self.figures_directory)
            model_count(self.df_solve_total, self.df_solve_slice,
                        arch, self.figures_directory)
            model_count_time(self.df_solve, arch, self.figures_directory)
            prediction_accuracies(self.deviations, arch,
                                  self.figures_directory)
            share_of_feature_variables(
                self.df_solve_unconstrained, arch, self.figures_directory)
            sloc(self.df_kconfig, arch, self.figures_directory)
            if arch == "all":
                total_features(self.df_features, self.figures_directory)


def linux_main(config: str):
    Linux(config)


if __name__ == "__main__":
    # CONFIGURABLE VARIABLES
    parser = ArgumentParser("Linux Figure Generator")
    parser.add_argument("--config", "-c", required=True, type=str)
    args = parser.parse_args()
    config = args.config if os.path.exists(args.config) else None
    if config:
        linux_main(config)
