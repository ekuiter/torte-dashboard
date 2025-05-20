import pandas as pd
import numpy as np
import os
import json
import pickle
from math import log10

### UTILITY FUNCTIONS

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
    big_sum = sum([int(value) for value in series if not pd.isna(value) and value])
    if big_sum > 0:
        return len(str(big_sum))

def write_object_to_file(obj, name):
    with open(name, "w") as fp:
        json.dump(obj, fp)


def read_json(path):
    with open(path) as json_data:
        return json.load(json_data)


def merge_metrics(new, old_path):
    old = read_json(old_path)

    for proj, metrics in new.items():
        for metric, values in metrics.items():
            for name, value in values.items():
                if proj not in old["projectData"]:
                    print(f"{proj} not in init.json")
                    continue
                if metric not in old["projectData"][proj]:
                    old["projectData"][proj][metric] = dict()
                old["projectData"][proj][metric][name] = value
    write_object_to_file(old, old_path)

class Linux:
    def __init__(self, linux_output_directory):
        self.output_directory = linux_output_directory
        self.df_kconfig = self.read_dataframe("kconfig")
        self.df_kconfig["year"] = self.df_kconfig["committer_date"].apply(
            lambda d: int(d.year)
        )
        self.df_architectures = self.read_dataframe("read-linux-architectures")
        self.df_architectures = self.df_architectures.sort_values(by="committer_date")
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
            self.df_architectures[["revision", "committer_date"]].drop_duplicates()
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
            self.df_solve_6h = pd.read_csv(f'{self.output_directory}/model-count-with-6h-timeout.csv', dtype={'model-count': 'string'})
            self.df_solve_6h = self.df_backbone_dimacs.merge(self.df_solve_6h)
            process_model_count(self.df_solve_6h)
            self.df_solve = pd.merge(self.df_solve, self.df_solve_6h[['revision','architecture', 'extractor', 'backbone.dimacs-analyzer']], indicator=True, how='outer') \
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
        df_solve_unconstrained = self.df_solve.merge(self.df_features)
        df_solve_unconstrained["model-count-unconstrained"] = df_solve_unconstrained.apply(
            lambda row: str(
                int(row["model-count"])
                * (2 ** int(row["unconstrained_bools"]))
                * (3 ** int(row["unconstrained_tristates"]))
            )
            if not pd.isna(row["model-count"]) and row["model-count"] != ""
            else pd.NA,
            axis=1,
        )
        df_solve_unconstrained["model-count-unconstrained-log10"] = (
            df_solve_unconstrained["model-count-unconstrained"]
            .fillna("")
            .map(big_log10)
            .replace(0, np.nan)
        )
        df_solve_unconstrained["similarity"] = df_solve_unconstrained.apply(
            lambda row: int(row["model-count"]) / int(row["model-count-unconstrained"])
            if not pd.isna(row["model-count"]) and row["model-count"] != ""
            else pd.NA,
            axis=1,
        )


        def unify_solvers(df, columns=['model-count-unconstrained-log10']):
            return df[['revision', 'committer_date', 'architecture', 'extractor', *columns]].drop_duplicates()

        def big_sum(series):
            big_sum = sum([int(value) for value in series if not pd.isna(value) and value])
            if big_sum > 0:
                return len(str(big_sum))
            
        self.df_solve_slice = df_solve_unconstrained[df_solve_unconstrained['year'] <= 2013]
        self.df_solve_failures = self.df_solve_slice.groupby(['extractor', 'revision', 'architecture'], dropna=False).agg({'model-count-unconstrained-log10': lambda x: (True in list(pd.notna(x)) or pd.NA)}).reset_index()
        self.df_solve_group = self.df_solve_failures.groupby(['extractor', 'revision'], dropna=False)
        self.df_solve_failures = (self.df_solve_group['model-count-unconstrained-log10'].size() - self.df_solve_group['model-count-unconstrained-log10'].count()).reset_index()
        self.df_solve_failures['is-upper-bound'] = self.df_solve_failures['model-count-unconstrained-log10'] == 0
        self.df_solve_failures = self.df_solve_failures.rename(columns={'model-count-unconstrained-log10': 'failures'})
        self.df_solve_total = unify_solvers(pd.merge(self.df_solve_slice, self.df_solve_failures), ['model-count-unconstrained', 'model-count-unconstrained-log10', 'is-upper-bound', 'failures', 'year'])
        self.df_solve_total = self.df_solve_total.groupby(['extractor', 'committer_date', 'year']).agg({'model-count-unconstrained': big_sum, 'is-upper-bound': 'min', 'failures': 'min'}).reset_index()
    
        self.keymap = {
            "#total_features": "total-features", 
            "#features": "features", 
            "backbone.dimacs-analyzer-time": "model-count-time",
            "model-count-unconstrained-log10": "model-count",
            "model-count-unconstrained": "model-count",
            "source_lines_of_code": "source_lines_of_code"
        }
        self.metrics = {f"linux/{arch}": dict() for arch in self.df_kconfig["architecture"].unique()}
        self.metrics["linux/all"] = dict()

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

    def differentiate_extractors(self,arch, df, sortBy, key, prefix, unit, apply_func=None):
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
                print(key,df["extractor"].unique(), extractor )
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
                    date_func=lambda ym: df_ex["committer_date"].dt.strftime("%Y") == ym.strftime("%Y")
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
            df_arch = self.df_solve_slice[self.df_solve_slice["architecture"]==arch]
            key = "backbone.dimacs-analyzer-time"
            extractor_values = self.differentiate_extractors(arch=arch,df=df_arch, sortBy="committer_date_unix", key=key, prefix="10^", unit="s", apply_func=lambda v: int(v)//1000000000)
            self.metrics[f"linux/{arch}"]["model-count-time"]= extractor_values

    def model_count_latest(self):
        archs = list(self.df_kconfig["architecture"].unique())
        archs.append("all")
        for arch in archs:
            df_arch = self.df_solve_slice[self.df_solve_slice["architecture"]==arch]
            key = "model-count-unconstrained-log10"
            sortBy = "committer_date_unix"
            if arch == 'all':
                df_arch = self.df_solve_total
                key = "model-count-unconstrained"
                sortBy = "committer_date"
            extractor_values = self.differentiate_extractors(arch=arch,df=df_arch, sortBy=sortBy, key=key, prefix="10^", unit="models", apply_func=lambda v: int(v))
            self.metrics[f"linux/{arch}"]["model-count"]= extractor_values
        
    def fill_metrics(self):
        self.total_features_latest()
        self.features_latest()
        self.sloc_latest()
        self.model_count_latest()
        self.model_count_time_latest()
        merge_metrics(self.metrics)

    def total_features_latest(self):
        extractor_values = self.differentiate_extractors(arch="all", df=self.df_total_features, sortBy="committer_date", key="#total_features", prefix="", unit="features", apply_func=lambda v: int(v))
        self.metrics["linux/all"]["total-features"] = extractor_values

    def features_latest(self):
        archs = list(self.df_kconfig["architecture"].unique())
        for architecture in archs:
            df = self.filter_for_architecture(self.df_features, architecture)
            extractor_values = self.differentiate_extractors(arch=architecture, df=df, sortBy="committer_date", key="#features", prefix="", unit="features", apply_func=lambda v: int(v))
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
                    date_func=lambda ym: df_arch["committer_date_readable"].str.contains(ym.strftime("%Y-%m"))
                )
                date = date.strftime("%B %d, %Y")
                date_prefix = "From"
                value = int(value.iloc[0][key])
            else: 
                value =  0
            self.metrics[f"linux/{arch}"][key]= {
                "currentValue": {
                    "value":f"{value} loc", 
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
                    "value": f"{prefix}{value} {unit})", 
                    "date": ym.strftime("%B %d, %Y")
                } 
        return history_vals
    
    def generate_figures(self):
        pass