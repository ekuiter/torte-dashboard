import plotly.express as px
import pandas as pd
import numpy as np
import os
import scipy
# helper functions for drawing plots


def estimate_group(group):
    print("\\hspace{2mm} " + group + " \\\\")


def estimate_trend(
    fig, color=None, color_value=None, xs=[], key=lambda x: x.timestamp()
):
    results = px.get_trendline_results(fig)
    if color is not None and color_value is not None:
        idx = [i for i, r in enumerate(
            results.iloc) if r[color] == color_value]
        if idx != []:
            idx = idx[0]
        else:
            idx = 0
    else:
        idx = 0
    intercept = results.iloc[idx]["px_fit_results"].params[0]
    slope = results.iloc[idx]["px_fit_results"].params[1]
    daily = slope * pd.to_timedelta(1, unit="D").total_seconds()
    weekly = slope * pd.to_timedelta(7, unit="D").total_seconds()
    monthly = slope * pd.to_timedelta(1, unit="D").total_seconds() * 30.437
    yearly = slope * pd.to_timedelta(1, unit="D").total_seconds() * 365.25
    return daily, weekly, monthly, yearly, [intercept + slope * key(x) for x in xs]


def committer_date_x_axis(fig, df, append_revision=True, step=1):
    axis = df[["committer_date", "revision"]].drop_duplicates()
    axis["year"] = axis["committer_date"].apply(lambda d: str(d.year))
    axis = axis.sort_values(by="committer_date").groupby(
        "year").nth(0).reset_index()
    fig.update_xaxes(
        ticktext=axis["year"].str.cat(
            "<br><sup>" + axis["revision"].str[1:] + "</sup>"
        )[1::step]
        if append_revision
        else axis["year"][::step],
        tickvals=axis["year"][1::step],
    )


def revision_x_axis(fig, df):
    axis = df[["committer_date", "revision"]].drop_duplicates()
    axis["year"] = axis["committer_date"].apply(lambda d: str(d.year))
    axis = axis.sort_values(by="committer_date").groupby(
        "year").nth(0).reset_index()
    fig.update_xaxes(ticktext=axis["year"], tickvals=axis["revision"])


def log10_y_axis(fig):
    fig.update_yaxes(tickprefix="10<sup>", ticksuffix="</sup>")


def percentage_y_axis(fig):
    fig.layout.yaxis.tickformat = ",.0%"


def format_percentage(value):
    return str(round(value * 100, 2)) + "%"


def committer_date_labels(dict={}):
    return {"committer_date": "Year<br><sup>First Release in Year</sup>"} | dict


def revision_labels(dict={}):
    return {"revision": "Year"} | dict


def style_legend(fig, position="topleft", xshift=0, yshift=0):
    if position == "topleft":
        fig.update_layout(
            legend=dict(yanchor="top", y=0.98 + yshift,
                        xanchor="left", x=0.01 + xshift)
        )
    elif position == "topright":
        fig.update_layout(
            legend=dict(
                yanchor="top", y=0.98 + yshift, xanchor="right", x=0.98 + xshift
            )
        )
    elif position == "bottomright":
        fig.update_layout(
            legend=dict(
                yanchor="bottom", y=0.01 + yshift, xanchor="right", x=0.98 + xshift
            )
        )
    elif position == "bottomleft":
        fig.update_layout(
            legend=dict(
                yanchor="bottom", y=0.01 + yshift, xanchor="left", x=0.01 + xshift
            )
        )
    else:
        fig.update_layout(showlegend=False)


def style_box(fig, legend_position="topleft", xshift=0, yshift=0):
    fig.update_traces(fillcolor="rgba(0,0,0,0)")
    fig.update_traces(line_width=1)
    fig.update_traces(marker_size=2)
    fig.update_layout(font_family="Linux Biolinum")
    style_legend(fig, legend_position, xshift, yshift)


def style_scatter(fig, marker_size=4, legend_position="topleft", xshift=0, yshift=0):
    if marker_size:
        fig.update_traces(marker_size=marker_size)
    style_legend(fig, legend_position, xshift, yshift)
    fig.update_layout(font_family="Linux Biolinum")


def plot_failures(
    fig, df, x, y, y_value, align="bottom", xref="x", font_size=10, textangle=270
):
    group = df.groupby(x, dropna=False)
    failures = (
        (group[y].size() - group[y].count())
        .reset_index()
        .rename(columns={y: f"{y}_failures"})
    )
    attempts = group[y].size().reset_index().rename(
        columns={y: f"{y}_attempts"})
    failures = pd.merge(failures, attempts)
    failures[f"{y}_text"] = (
        failures[f"{y}_failures"].astype(str)
        + " ("
        + (failures[f"{y}_failures"] / failures[f"{y}_attempts"]).apply(
            lambda v: "{0:.1f}%".format(v * 100)
        )
        + ")"
    )
    for row in range(len(failures)):
        text = failures.at[row, f"{y}_text"]
        text = "" if failures.at[row, f"{y}_failures"] == 0 else text
        fig.add_annotation(
            x=failures.at[row, x],
            y=y_value,
            text=text,
            showarrow=False,
            font_size=font_size,
            textangle=textangle,
            align="left" if align == "bottom" else "right",
            yanchor="bottom" if align == "bottom" else "top",
            yshift=5 if align == "bottom" else -5,
            font_color="gray",
            xref=xref,
        )


def cohens_d(d1, d2):
    # uses pooled standard deviation
    n1, n2 = len(d1), len(d2)
    s1, s2 = np.var(d1, ddof=1), np.var(d2, ddof=1)
    s = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    u1, u2 = np.mean(d1), np.mean(d2)
    return (u1 - u2) / s


def wilcoxon_test(df, column_a, column_b):
    # if the same values are returned for many inputs, refer to https://stats.stackexchange.com/q/232927
    a = df[column_a][~df[column_a].isna()]
    b = df[column_b][~df[column_b].isna()]
    d = a - b
    results = scipy.stats.wilcoxon(d, method="approx")
    p = results.pvalue
    # adapted from https://stats.stackexchange.com/q/133077
    r = np.abs(results.zstatistic / np.sqrt(len(d) * 2))
    return p, r


def style_p_values(
    fig, brackets, scale=0, _format=dict(interline=0.07, text_height=1.07, color="gray")
):
    # adapted from https://stackoverflow.com/q/67505252
    for entry in brackets:
        first_column, second_column, y, results = entry
        y_range = [1.01 + y * _format["interline"],
                   1.02 + y * _format["interline"]]
        p, r = results
        if p >= 0.05:
            symbol = "ns"
        elif p >= 0.01:
            symbol = "*"
        elif p >= 0.001:
            symbol = "**"
        else:
            symbol = "***"
        first_column = first_column - scale
        second_column = second_column + scale
        fig.add_shape(
            type="line",
            xref="x",
            yref="y domain",
            x0=first_column,
            y0=y_range[0],
            x1=first_column,
            y1=y_range[1],
            line=dict(
                color=_format["color"],
                width=2,
            ),
        )
        fig.add_shape(
            type="line",
            xref="x",
            yref="y domain",
            x0=first_column,
            y0=y_range[1],
            x1=second_column,
            y1=y_range[1],
            line=dict(
                color=_format["color"],
                width=2,
            ),
        )
        fig.add_shape(
            type="line",
            xref="x",
            yref="y domain",
            x0=second_column,
            y0=y_range[0],
            x1=second_column,
            y1=y_range[1],
            line=dict(
                color=_format["color"],
                width=2,
            ),
        )
        fig.add_annotation(
            dict(
                font=dict(color=_format["color"], size=14),
                x=(first_column + second_column) / 2,
                y=y_range[1] * _format["text_height"],
                showarrow=False,
                text=symbol + " <sup>(" + str(round(r, 2)) + ")</sup>",
                textangle=0,
                xref="x",
                yref="y domain",
            )
        )
    return fig


def bracket_for(i, j, xshift, y, results):
    return [i + xshift, j + xshift, y, results]


def filter_extractor(df, extractor):
    return df[df["extractor"] == extractor]


def annotate_value(
    fig,
    x,
    y,
    subplot,
    prefix,
    ax,
    ay,
    xanchor,
    df,
    fn=lambda prefix, y: prefix + ": " +
        format(round(y), ",") if y > 0 else prefix,
):
    if df.empty:
        return
    if isinstance(x, str):
        x = df[x].iat[0]
    if isinstance(y, str):
        y = df[y].iat[0]
    fig.add_annotation(
        xref="x" + str(subplot),
        yref="y" + str(subplot),
        x=x,
        y=y,
        ax=ax,
        ay=ay,
        xanchor=xanchor,
        text=fn(prefix, y),
    )


def show(fig, figures_directory, name, plot_category, margin=None):
    if margin:
        fig.update_layout(margin=margin)
    else:
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    if not os.path.exists(figures_directory):
        os.mkdir(figures_directory)
    if not os.path.exists(f"{figures_directory}/{plot_category}"):
        os.mkdir(f"{figures_directory}/{plot_category}")
    fig.write_html(
        f"{figures_directory}/{plot_category}/{name}.html", config={"responsive": True}
    )


def jaccard_similarity(df_features, architecture, output_dir):
    # # Jaccard similarity to features (RQ2)
    if architecture != "all":
        df_features = df_features[df_features["architecture"] == architecture]
    df_features_long = pd.melt(
        df_features,
        id_vars=['extractor'],
        value_vars=['extracted_features_jaccard', 'all_variables_jaccard', 'variables_jaccard',
                    'feature_variables_jaccard', 'undead_feature_variables_jaccard', 'all_feature_variables_jaccard',
                    'features_jaccard']
    )
    df_features_long.replace(
        {'variable': 'extracted_features_jaccard'}, 'F<sub>extracted</sub>', inplace=True)
    df_features_long.replace(
        {'variable': 'all_variables_jaccard'}, 'V<sub>all</sub>', inplace=True)
    df_features_long.replace(
        {'variable': 'variables_jaccard'}, 'V', inplace=True)
    df_features_long.replace(
        {'variable': 'feature_variables_jaccard'}, 'FV', inplace=True)
    df_features_long.replace(
        {'variable': 'undead_feature_variables_jaccard'}, 'FV<sub>undead</sub>', inplace=True)
    df_features_long.replace(
        {'variable': 'all_feature_variables_jaccard'}, 'F<sub>all</sub>', inplace=True)
    df_features_long.replace(
        {'variable': 'features_jaccard'}, 'F', inplace=True)
    if df_features_long["value"].empty:
        print(
            f"'Jaccard Similarity' plot for project/architecture 'Linux/{architecture}' could not be created because 'df_features_long[\"value\"]' is empty.")
        return
    fig = px.box(
        df_features_long,
        x='variable',
        y='value',
        range_y=[0, 1],
        color='extractor',
        facet_col='extractor',
        labels={'value': f'Jaccard Similarity to Features (F) ({architecture})',
                'variable': 'Set of Candidate Features', 'extractor': 'Extractor'},
        category_orders={'variable': ['F<sub>extracted</sub>', 'V<sub>all</sub>', 'V', 'FV', 'FV<sub>undead</sub>', 'F<sub>all</sub>', 'F'],
                         'extractor': ['KConfigReader', 'KClause']},
    )
    fig.update_traces(width=0.5)
    percentage_y_axis(fig)
    style_box(fig, legend_position=None)
    show(fig,
         output_dir,
         f'jaccard-similarity-linux-{architecture}',
         margin=dict(l=0, r=0, t=20, b=0),
         plot_category="jaccard-similarity",
         )


def configuration_similarity(df_solve_unconstrained, architecture, output_dir):
    if architecture != "all":
        df_solve_unconstrained = df_solve_unconstrained[df_solve_unconstrained["architecture"] == architecture]
    if df_solve_unconstrained["similarity"].empty:
        print(
            f"'Configuration Similarity' plot for project/architecture 'Linux/{architecture}' could not be created because 'df_solve_unconstrained[\"similarity\"]' is empty.")
        return
    fig = px.box(
        df_solve_unconstrained,
        y='similarity',
        color='extractor',
        facet_col='extractor',
        labels={
            'similarity': f'Ratio of #C<sub>min</sub> to #C (log10) ({architecture})'},
        log_y=True,
        category_orders={'extractor': ['KConfigReader', 'KClause']}
    )
    fig.for_each_annotation(lambda a: a.update(
        text='KCR' if a.text.split("=")[1] == 'KConfigReader' else 'KCl'))
    fig.update_traces(width=0.5)
    fig.update_yaxes(tickvals=[1e0, 1e-3, 1e-6, 1e-9, 1e-12, 1e-15], ticktext=['10<sup>0</sup>',
                                                                               '10<sup>-3</sup>', '10<sup>-6</sup>', '10<sup>-9</sup>', '10<sup>-12</sup>', '10<sup>-15</sup>'])
    style_box(fig, legend_position=None)
    show(
        fig, output_dir, f'configuration-similarity-linux-{architecture}', margin=dict(l=0, r=0, t=20, b=0), plot_category="configuration-similarity")

# share of all feature variables


def share_of_feature_variables(df_features, architecture, output_dir):
    if architecture != "all":
        df_features = df_features[df_features["architecture"] == architecture]
    df_features_long = pd.melt(
        df_features[~df_features['#features'].isna()].assign(**{
            '#dead_feature_variables': df_features['#dead_feature_variables'] / df_features['#ALL_feature_variables'],
            '#core_feature_variables': df_features['#core_feature_variables'] / df_features['#ALL_feature_variables'],
            '#constrained_feature_variables': df_features['#constrained_feature_variables'] / df_features['#ALL_feature_variables'],
            '#unconstrained_feature_variables': df_features['#unconstrained_feature_variables'] / df_features['#ALL_feature_variables'],
        }),
        id_vars=['extractor'],
        value_vars=['#dead_feature_variables', '#core_feature_variables',
                    '#constrained_feature_variables', '#unconstrained_feature_variables'],
    )
    df_features_long.replace(
        {'variable': '#dead_feature_variables'}, 'FV<sub>dead</sub>', inplace=True)
    df_features_long.replace(
        {'variable': '#core_feature_variables'}, 'FV<sub>core</sub>', inplace=True)
    df_features_long.replace(
        {'variable': '#constrained_feature_variables'}, 'FV<sub>constrained</sub>', inplace=True)
    df_features_long.replace(
        {'variable': '#unconstrained_feature_variables'}, 'F<sub>unconstrained</sub>', inplace=True)

    if df_features_long["value"].empty:
        print(
            f"'Share of Feature Variables' plot for project/architecture 'Linux/{architecture}' could not be created because 'df_features_long[\"value\"]' is empty.")
        return
    fig = px.box(
        df_features_long,
        x='variable',
        y='value',
        range_y=[0, 1],
        color='extractor',
        labels={'value': f'Share of All Feature Variables (FV<sub>all</sub>) ({architecture})',
                'variable': 'Level of Feature Configurability', 'extractor': 'Extractor'},
        category_orders={'variable': ['FV<sub>core</sub>', 'FV<sub>dead</sub>', 'F<sub>unconstrained</sub>', 'FV<sub>constrained</sub>'],
                         'extractor': ['KConfigReader', 'KClause']}
    )
    percentage_y_axis(fig)
    style_box(fig, legend_position='topleft')
    show(fig, output_dir,
         f'share-of-feature-variables-linux-{architecture}', plot_category="share-of-feature-variables")


def total_features(df_features, output_dir):
    if df_features["#features"].empty:
        print(
            f"'#Features' plot for project/architecture 'Linux/all' could not be created because 'df_features[\"#total_features\"]' is empty.")
        return
    fig = px.scatter(
        df_features.sort_values(by='committer_date'),
        x='committer_date',
        y='#total_features',
        facet_col='extractor',
        labels={
            '#total_features': '#Features (Total)', 'extractor': 'Extractor', 'committer_date': 'Year'},
        category_orders={'extractor': ['KConfigReader', 'KClause']}
    )
    style_scatter(fig)
    def fn(prefix, y): return format(round(y), ',')
    annotate_value(fig, 'committer_date', 0, 1, 'v2.5.45', 0, -15,
                   'center', df_features[df_features['revision'] == 'v2.5.45'])
    annotate_value(fig, 'committer_date', 0, 1, 'v6.11', -10, -15,
                   'center', df_features[df_features['revision'] == 'v6.11'])
    annotate_value(fig, 'committer_date', '#total_features', 1, 'KConfigReader', 40, 0, 'left',
                   df_features[(df_features['extractor'] == 'KConfigReader') & (df_features['revision'] == 'v2.5.45')], fn)
    annotate_value(fig, 'committer_date', '#total_features', 1, 'KConfigReader', -10, 30, 'right',
                   df_features[(df_features['extractor'] == 'KConfigReader') & (df_features['revision'] == 'v6.11')], fn)
    annotate_value(fig, 'committer_date', 0, 2, 'v2.5.45', 0, -15,
                   'center', df_features[df_features['revision'] == 'v2.5.45'])
    annotate_value(fig, 'committer_date', 0, 2, 'v6.11', -10, -15,
                   'center', df_features[df_features['revision'] == 'v6.11'])
    annotate_value(fig, 'committer_date', '#total_features', 2, 'KClause', 40, 0, 'left',
                   df_features[(df_features['extractor'] == 'KClause') & (df_features['revision'] == 'v2.5.45')], fn)
    annotate_value(fig, 'committer_date', '#total_features', 2, 'KClause', -10, 30, 'right',
                   df_features[(df_features['extractor'] == 'KClause') & (df_features['revision'] == 'v6.11')], fn)
    fig.update_yaxes(tickprefix="   ")
    fig.update_xaxes(range=["2002-01-01", "2024-12-01"])
    fig.update_yaxes(range=[0, 20500])
    show(
        fig,
        output_dir,
        f"total-features-linux-all",
        plot_category="total-features",
        margin=dict(l=0, r=0, t=20, b=0),
    )


def features(df_features, architecture, output_dir):
    df_features = df_features[df_features["architecture"] == architecture]
    if df_features["#features"].empty:
        print(
            f"'#Features' plot for project/architecture 'Linux/{architecture}' could not be created because 'df_features[\"#features\"]' is empty.")
        return
    fig = px.scatter(
        df_features,
        x='committer_date',
        y=f'#features',
        color='architecture',
        labels={f'#features': f'#Features (Arch.) ({architecture})',
                'extractor': 'Extractor', 'committer_date': 'Year'},
        hover_data=['revision', 'architecture'],
        facet_col='extractor',
        category_orders={'extractor': ['KConfigReader', 'KClause']}
    )
    style_scatter(fig, legend_position=None, marker_size=2.5)
    annotate_value(fig, 'committer_date', 0, 1, 'v4.16', 0, -15,
                   'center', df_features[df_features['revision'] == 'v4.16'])
    annotate_value(fig, 'committer_date', 0, 1, 'v6.11', -10, -15,
                   'center', df_features[df_features['revision'] == 'v6.11'])
    annotate_value(fig, 'committer_date', '#features', 1, 'arm', -10, -20, 'right', df_features[(
        df_features['extractor'] == 'KConfigReader') & (df_features['architecture'] == 'arm') & (df_features['revision'] == 'v6.11')],)
    annotate_value(fig, 'committer_date', '#features', 1, 'x86', -100, -20, 'right', df_features[(
        df_features['extractor'] == 'KConfigReader') & (df_features['architecture'] == 'x86') & (df_features['revision'] == 'v6.11')])
    annotate_value(fig, 'committer_date', '#features', 1, 'arm64', -120, 0, 'right', df_features[(
        df_features['extractor'] == 'KConfigReader') & (df_features['architecture'] == 'arm64') & (df_features['revision'] == 'v6.11')])
    annotate_value(fig, 'committer_date', '#features', 1, 'nios2', -5, 40, 'right', df_features[(
        df_features['extractor'] == 'KConfigReader') & (df_features['architecture'] == 'nios2') & (df_features['revision'] == 'v6.11')])
    annotate_value(fig, 'committer_date', '#features', 1, 'score', 20, 0, 'left',   df_features[(
        df_features['extractor'] == 'KConfigReader') & (df_features['architecture'] == 'score') & (df_features['revision'] == 'v4.16')])
    annotate_value(fig, 'committer_date', 0, 2, 'v4.16', 0, -15,
                   'center', df_features[df_features['revision'] == 'v4.16'])
    annotate_value(fig, 'committer_date', 0, 2, 'v6.11', -10, -15,
                   'center', df_features[df_features['revision'] == 'v6.11'])
    annotate_value(fig, 'committer_date', '#features', 2, 'arm', -10, -20, 'right', df_features[(
        df_features['extractor'] == 'KClause') & (df_features['architecture'] == 'arm') & (df_features['revision'] == 'v6.11')])
    annotate_value(fig, 'committer_date', '#features', 2, 'x86', -100, -20, 'right', df_features[(
        df_features['extractor'] == 'KClause') & (df_features['architecture'] == 'x86') & (df_features['revision'] == 'v6.11')])
    annotate_value(fig, 'committer_date', '#features', 2, 'arm64', -120, 0, 'right', df_features[(
        df_features['extractor'] == 'KClause') & (df_features['architecture'] == 'arm64') & (df_features['revision'] == 'v6.11')])
    annotate_value(fig, 'committer_date', '#features', 2, 'nios2', -5, 40, 'right', df_features[(
        df_features['extractor'] == 'KClause') & (df_features['architecture'] == 'nios2') & (df_features['revision'] == 'v6.11')])
    annotate_value(fig, 'committer_date', '#features', 2, 'score', 20, 0, 'left',   df_features[(
        df_features['extractor'] == 'KClause') & (df_features['architecture'] == 'score') & (df_features['revision'] == 'v4.16')])
    fig.update_yaxes(tickprefix="    ")
    fig.update_xaxes(range=["2002-01-01", "2024-12-01"])
    fig.update_yaxes(range=[0, 21000])
    show(
        fig,
        output_dir,
        f"features-linux-{architecture}",
        plot_category="features",
        margin=dict(l=0, r=0, t=20, b=0),
    )


def model_count_time(df_solve, architecture, output_dir):
    if architecture != "all":
        df_solve = df_solve[df_solve["architecture"] == architecture]
    df_solve_slice = df_solve[~df_solve['model-count-log10'].isna()]
    if df_solve_slice.empty:
        print(
            f"'Time for Counting' plot for project/architecture 'Linux/{architecture}' could not be created because 'df_solve_slice[\"model-count-log10\"]' is empty.")
        return False
    fig = px.scatter(
        df_solve_slice,
        x=df_solve_slice['committer_date'],
        y=df_solve_slice['backbone.dimacs-analyzer-time'] / 1000000000,
        color='architecture',
        labels={'extractor': 'Extractor',
                'y': f'Time for Counting (log<sub>10</sub> s) ({architecture})', 'committer_date': 'Year'},
        facet_col='extractor',
        facet_row='backbone.dimacs-analyzer',
        log_y=True
    )
    style_scatter(fig, legend_position=None, marker_size=2.5)
    show(fig, output_dir, f'model-count-time-linux-{architecture}', margin=dict(
        l=0, r=0, t=20, b=0), plot_category="model-count-time")


def big_sum(series):
    big_sum = sum([int(value)
                  for value in series if not pd.isna(value) and value])
    if big_sum > 0:
        return len(str(big_sum))


def model_count(df_solve_total, df_solve_slice, architecture, output_dir):
    if architecture == "all":
        _mct(df_solve_total, df_solve_slice, output_dir)
        return
    df_solve_slice = df_solve_slice[df_solve_slice["architecture"]
                                    == architecture]
    if df_solve_slice["model-count-unconstrained-log10"].empty:
        print(
            f"#Configuration plot for project/architecture 'Linux/{architecture}' could not be created because 'df_solve_slice[\"model-count-unconstrained-log10\"]' is empty.")
        return
    fig = px.scatter(
        df_solve_slice,
        x='committer_date',
        y='model-count-unconstrained-log10',
        color='architecture',
        labels={'model-count-unconstrained-log10':
                '#Configurations (Arch., log<sub>10</sub>)', 'committer_date': 'Year', 'extractor': 'Extractor'},
        hover_data=['revision', 'architecture'],
        facet_col='extractor',
        category_orders={'extractor': ['KConfigReader', 'KClause']}
    )
    log10_y_axis(fig)
    style_scatter(fig, legend_position=None, marker_size=2.5)
    def fn1(prefix, y): return prefix
    def fn2(prefix, y): return f'{prefix}: 10<sup>{round(y)}</sup>'
    annotate_value(fig, 'committer_date', 0, 1, 'v2.6.13', 0, -15, 'center',
                   df_solve_slice[df_solve_slice['revision'] == 'v2.6.13'], fn1)
    annotate_value(fig, 'committer_date', 0, 1, 'v2.6.39', 0, -15, 'center',
                   df_solve_slice[df_solve_slice['revision'] == 'v2.6.39'], fn1)
    annotate_value(fig, 'committer_date', 'model-count-unconstrained-log10', 1, 'i386', 0, -20, 'center',
                   df_solve_slice[(df_solve_slice['extractor'] == 'KConfigReader') & (df_solve_slice['architecture'] == 'i386') & (df_solve_slice['revision'] == 'v2.6.13')].dropna(), fn2)
    annotate_value(fig, 'committer_date', 'model-count-unconstrained-log10', 1, 'h8300', 10, 10, 'left',
                   df_solve_slice[(df_solve_slice['extractor'] == 'KConfigReader') & (df_solve_slice['architecture'] == 's390') & (df_solve_slice['revision'] == 'v2.6.39')].dropna(), fn2)
    annotate_value(fig, 'committer_date', 0, 2, 'v2.6.23', 0, -15, 'center',
                   df_solve_slice[df_solve_slice['revision'] == 'v2.6.23'], fn1)
    annotate_value(fig, 'committer_date', 0, 2, 'v3.10', 0, -15, 'center',
                   df_solve_slice[df_solve_slice['revision'] == 'v3.10'], fn1)
    annotate_value(fig, 'committer_date', 'model-count-unconstrained-log10', 2, 'i386', 0, -20, 'center',
                   df_solve_slice[(df_solve_slice['extractor'] == 'KClause') & (df_solve_slice['architecture'] == 'i386') & (df_solve_slice['revision'] == 'v2.6.23') & (df_solve_slice['backbone.dimacs-analyzer'] == 'model-counting-competition-2022/SharpSAT-td+Arjun/SharpSAT-td+Arjun.sh')].dropna(), fn2)
    annotate_value(fig, 'committer_date', 'model-count-unconstrained-log10', 2, 'h8300', 10, 10, 'left',
                   df_solve_slice[(df_solve_slice['extractor'] == 'KClause') & (df_solve_slice['architecture'] == 'h8300') & (df_solve_slice['revision'] == 'v3.10')].dropna(), fn2)
    fig.update_xaxes(range=["2002-01-01", "2024-12-01"])
    fig.update_yaxes(range=[0, 1050], dtick=200)
    show(fig, output_dir, f'model-count-linux-{architecture}', margin=dict(
        l=0, r=0, t=2, b=0), plot_category="model-count")


def _mct(df_solve_total, df_solve_slice, output_dir):
    if df_solve_total["model-count-unconstrained"].empty:
        print(
            f"#Configuration plot for project/architecture 'Linux/{all}' could not be created because 'df_solve_total[\"model-count-unconstrained\"]' is empty.")
        return
    fig = px.scatter(
        df_solve_total.replace(True, 'Exact').replace(False, 'Lower Bound'),
        x='committer_date',
        y='model-count-unconstrained',
        symbol='is-upper-bound',
        symbol_sequence=['circle', 'triangle-up-open'],
        facet_col='extractor',
        labels=revision_labels({'model-count-unconstrained': '#Configurations (Total, log<sub>10</sub>)',
                               'extractor': 'Extractor', 'is-upper-bound': 'Kind of Bound', 'committer_date': 'Year'}),
        category_orders={'extractor': ['KConfigReader', 'KClause']}
    )
    log10_y_axis(fig)
    style_scatter(fig, legend_position='topright', xshift=0.01, yshift=0.03)
    fig.update_traces(marker_line_color='rgba(0,0,0,0)')
    def fn1(prefix, y): return prefix
    def fn2(prefix, y): return '10<sup>' + format(round(y), ',') + '</sup>'
    annotate_value(fig, 'committer_date', 0, 1, 'v2.5.45', 0, -15, 'center',
                   df_solve_slice[df_solve_slice['revision'] == 'v2.5.45'], fn1)
    annotate_value(fig, 'committer_date', 0, 1, 'v2.6.7', 0, -30, 'center',
                   df_solve_slice[df_solve_slice['revision'] == 'v2.6.7'], fn1)
    annotate_value(fig, 'committer_date', 0, 1, 'v2.6.13', 5, -15, 'center',
                   df_solve_slice[df_solve_slice['revision'] == 'v2.6.13'], fn1)
    annotate_value(fig, 'committer_date', 'model-count-unconstrained', 1, 'KCR', 15, 0, 'left',
                   df_solve_slice[(df_solve_slice['extractor'] == 'KConfigReader') & (
                       df_solve_slice['revision'] == 'v2.5.45')]
                   .groupby(['extractor', 'committer_date']).agg({'model-count-unconstrained': big_sum}).reset_index(), fn2)
    annotate_value(fig, 'committer_date', 'model-count-unconstrained', 1, 'KCR', 10, 10, 'left',
                   df_solve_slice[(df_solve_slice['extractor'] == 'KConfigReader') & (
                       df_solve_slice['revision'] == 'v2.6.7')]
                   .groupby(['extractor', 'committer_date']).agg({'model-count-unconstrained': big_sum}).reset_index(), fn2)
    annotate_value(fig, 'committer_date', 'model-count-unconstrained', 1, 'KCR', 15, -10, 'left',
                   df_solve_slice[(df_solve_slice['extractor'] == 'KConfigReader') & (
                       df_solve_slice['revision'] == 'v2.6.13')]
                   .groupby(['extractor', 'committer_date']).agg({'model-count-unconstrained': big_sum}).reset_index(), fn2)
    annotate_value(fig, 'committer_date', 0, 2, 'v2.5.45', 0, -15, 'center',
                   df_solve_slice[df_solve_slice['revision'] == 'v2.5.45'], fn1)
    annotate_value(fig, 'committer_date', 0, 2, 'v2.6.23', 0, -15, 'center',
                   df_solve_slice[df_solve_slice['revision'] == 'v2.6.23'], fn1)
    annotate_value(fig, 'committer_date', 'model-count-unconstrained', 2, 'KCl', 25, 5, 'left',
                   df_solve_slice[(df_solve_slice['extractor'] == 'KClause') & (
                       df_solve_slice['revision'] == 'v2.5.45')]
                   .groupby(['extractor', 'committer_date']).agg({'model-count-unconstrained': big_sum}).reset_index(), fn2)
    annotate_value(fig, 'committer_date', 'model-count-unconstrained', 2, 'KCl', 15, -15, 'left',
                   df_solve_slice[(df_solve_slice['extractor'] == 'KClause') & (
                       df_solve_slice['revision'] == 'v2.6.23')]
                   .groupby(['extractor', 'committer_date']).agg({'model-count-unconstrained': big_sum}).reset_index(), fn2)
    fig.update_xaxes(range=["2002-01-01", "2024-12-01"])
    fig.update_yaxes(range=[0, 1050], dtick=200)
    show(fig, output_dir, 'model-count-linux-all', plot_category="model-count")


def sloc(df_kconfig, architecture, output_dir):
    if df_kconfig.dropna(subset=["source_lines_of_code"]).empty:
        print(
            f"#SLOC plot for project/architecture 'Linux/{architecture}' could not be created because 'df_kconfig[\"source_lines_of_code\"]' is empty.")
        return
    if architecture != "all":
        df_kconfig = df_kconfig[df_kconfig["architecture"] == architecture]
    fig = px.scatter(
        df_kconfig,
        x="committer_date",
        y="source_lines_of_code",
        labels={
            "source_lines_of_code": "Number of Source Lines of Code",
            "committer_date": "Year",
        },
        hover_data=["revision"],
    )
    style_scatter(fig)
    show(fig, output_dir,
         f"source_lines_of_code-linux-{architecture}", plot_category="source_lines_of_code")


def feature_evolution(df_features, architecture, output_dir):
    f = "total"
    if architecture != "all":
        df_features = df_features[df_features["architecture"] == architecture]
        f = "arch"
    for df in [df_features[df_features['year'] >= 2005]]:
        for (added, removed, df, label, file, y_color) in [('#total_added_features', '#total_removed_features', df[['extractor', '#total_added_features', '#total_removed_features']].drop_duplicates(), 'Change in #Features (log<sub>10</sub>)', 'total', 'black'), ('#added_features', '#removed_features', df, ' ', 'arch', 'white')]:
            df_features_long = pd.melt(
                df,
                id_vars=['extractor'],
                value_vars=[added, removed]
            )
            df_features_long.replace(
                {'variable': added}, 'Added', inplace=True)
            df_features_long.replace(
                {'variable': removed}, 'Removed', inplace=True)
            df_features_long.replace({'value': 0}, 1, inplace=True)
            if df_features_long["value"].empty:
                print(
                    f"Feature evolution plot for project/architecture Linux/'{architecture}' could not be created because 'df_features_long[\"value\"]' is empty.")
                continue
            fig = px.box(
                df_features_long,
                x='variable',
                y='value',
                color='extractor',
                facet_col='extractor',
                facet_col_spacing=0.1,
                labels={'value': label, 'variable': '',
                        'extractor': 'Extractor'},
                log_y=True,
                category_orders={'extractor': ['KConfigReader', 'KClause']}
            )
            fig.for_each_annotation(lambda a: a.update(text='Extractor=KCR' if a.text.split(
                "=")[1] == 'KConfigReader' else 'Extractor=KCl'))
            fig.update_traces(width=0.5)
            fig.update_yaxes(tickvals=[1, 2, 10, 100, 1000], ticktext=['0', '10<sup>0</sup>', '10<sup>1</sup>',
                             '10<sup>2</sup>', '10<sup>3</sup>'], range=[0, 3.7], tickfont=dict(color=y_color))
            style_box(fig, legend_position=None)
            show(fig, output_dir, f'feature-evolution-{f}-linux-{architecture}', margin=dict(
                l=0, r=0, t=21, b=0), plot_category=f"feature-evolution-{f}")


def plot_configuration_evolution(df, architecture, y, output_dir):
    color = "white"
    f = "arch"
    if architecture == "all":
        color = "black"
        df = df[df["architecture"] == architecture]
        f = "total"
    df['x'] = ' '
    fig = px.box(
        df,
        x='x',
        y=y,
        color='extractor',
        facet_col='extractor',
        labels={'model-count-unconstrained-log10': ' ', 'model-count-unconstrained':
                f' Scale of #Configurations (log<sub>10</sub>) ({architecture})', 'extractor': 'Extractor', 'x': ''},
        category_orders={'extractor': ['KConfigReader', 'KClause']}
    )
    fig.for_each_annotation(lambda a: a.update(
        text='KCR' if a.text.split("=")[1] == 'KConfigReader' else 'KCl'))
    fig.update_traces(width=0.5)
    fig.update_yaxes(range=[-277, 180], tickfont=dict(color=color))
    log10_y_axis(fig)
    style_box(fig, legend_position=None)
    show(fig, output_dir,  f'configuration-evolution-{f}-linux-{architecture}', height=260, width=120, margin=dict(
        l=0, r=0, t=21, b=0), plot_category=f"configuration-evoluation-{f}")


def prediction_accuracies(deviations, architecture, output_dir):
    if architecture != "all":
        deviations = deviations[deviations["architecture"] == architecture]
    for metric in ['features', 'configurations', 'configurations-by-features']:
        df_tmp = deviations[deviations['metric'] == metric]
        if df_tmp.empty:
            print(
                f"Prediction Accuracy plot for project/architecture Linux/'{architecture}' could not be created because 'deviations[\"{metric}\"]' is empty.")
            continue
        fig = px.box(
            deviations[deviations['metric'] == metric],
            x='is-total',
            y='deviation',
            color='extractor',
            facet_col='extractor',
            facet_col_spacing=0.1,
            labels={'deviation': f'Relative Deviation ({architecture})' if metric ==
                    'features' else '', 'extractor': 'Extractor'},
        )
        fig.update_traces(width=0.5)
        fig.update_yaxes(range=[-1.1, 1.1])
        percentage_y_axis(fig)
        style_box(fig, legend_position=None)
        show(fig, output_dir, f'prediction-accuracy-{metric}-linux-{architecture}', margin=dict(
            l=0, r=0, t=21, b=0), plot_category=f"prediction-accuracy-{metric}")

def plot_configuration_evolution(file, df, y, architecture, output_dir, y_color='black'):
    df['x'] = ' '
    if df[y].empty:
        print(
            f"'Configuration Evolution' plot for project/architecture Linux/'{architecture}' could not be created because 'df[\"{y}\"]' is empty.")
        return
    fig = px.box(
        df,
        x='x',
        y=y,
        color='extractor',
        facet_col='extractor',
        labels={'model-count-unconstrained-log10': ' ', 'model-count-unconstrained': ' Scale of #Configurations (log<sub>10</sub>)', 'extractor': 'Extractor', 'x': ''},
        category_orders={'extractor': ['KConfigReader', 'KClause']}
    )
    fig.for_each_annotation(lambda a: a.update(text='KCR' if a.text.split("=")[1] == 'KConfigReader' else 'KCl'))
    fig.update_traces(width=0.5)
    fig.update_yaxes(range=[-277, 180], tickfont=dict(color=y_color))
    log10_y_axis(fig)
    style_box(fig, legend_position=None)
    show(fig, output_dir, f'configuration-evolution-{file}-linux-{architecture}', plot_category=f"configuration-evolution-{file}")


def configuration_evolution(df_solve_total, df_solve_unconstrained_diff, arch, output_dir):
    if arch == "all":
        df_solve_total_diff = df_solve_total.copy().sort_values(by='committer_date')
        df_solve_total_diff = df_solve_total_diff[df_solve_total_diff['is-upper-bound']]
        for extractor in set(df_solve_total_diff['extractor']):
                df_solve_total_diff.loc[(df_solve_total_diff['extractor'] == extractor), ['model-count-unconstrained']] = df_solve_total_diff[(df_solve_total_diff['extractor'] == extractor)]['model-count-unconstrained'].diff()
        plot_configuration_evolution('total', df_solve_total_diff, 'model-count-unconstrained', arch, output_dir)
    else:
        for extractor in set(df_solve_unconstrained_diff['extractor']):
            for architecture in set(df_solve_unconstrained_diff['architecture']):
                df_solve_unconstrained_diff.loc[(df_solve_unconstrained_diff['architecture'] == architecture) & (df_solve_unconstrained_diff['extractor'] == extractor), ['model-count-unconstrained-log10']] = df_solve_unconstrained_diff[(df_solve_unconstrained_diff['architecture'] == architecture) & (df_solve_unconstrained_diff['extractor'] == extractor)]['model-count-unconstrained-log10'].diff()
        plot_configuration_evolution('arch', df_solve_unconstrained_diff, 'model-count-unconstrained-log10', arch, output_dir, 'white')
