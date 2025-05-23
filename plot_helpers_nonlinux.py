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
        idx = [i for i, r in enumerate(results.iloc) if r[color] == color_value]
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
    axis = axis.sort_values(by="committer_date").groupby("year").nth(0).reset_index()
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
    axis = axis.sort_values(by="committer_date").groupby("year").nth(0).reset_index()
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
            legend=dict(yanchor="top", y=0.98 + yshift, xanchor="left", x=0.01 + xshift)
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
    attempts = group[y].size().reset_index().rename(columns={y: f"{y}_attempts"})
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
        y_range = [1.01 + y * _format["interline"], 1.02 + y * _format["interline"]]
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
    fn=lambda prefix, y: prefix + ": " + format(round(y), ",") if y > 0 else prefix,
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
    if not os.path.exists(f"{figures_directory}/{plot_category}"):
        os.mkdir(f"{figures_directory}/{plot_category}")
    fig.write_html(
        f"{figures_directory}/{plot_category}/{name}.html", config={"responsive": True}
    )


def total_features(df, project, output_dir):
    if df.dropna(subset=["model-features"]).empty:
        print(
            f"'Total Features' plot for project '{project}' could not be created because 'df[\"model-features\"]' is empty.")
        return
    fig = px.scatter(
        df.sort_values(by="committer_date"),
        x="committer_date",
        y="model-features",
        labels={"model-features": "#Features (Total)", "committer_date": "Year"},
    )
    style_scatter(fig)
    fig.update_yaxes(tickprefix="   ")
    fig.update_xaxes(range=["2002-01-01", "2024-12-01"])
    show(
        fig,
        output_dir,
        f"total-features-{project}",
        plot_category="total-features",
        margin=dict(l=0, r=0, t=20, b=0),
    )


def model_count_time(df, project, output_dir):
    if df.dropna(subset=["model-time"]).empty:
        print(
            f"'Time for Counting' plot for project '{project}' could not be created because 'df[\"model-time\"]' is empty.")
        return
    fig = px.scatter(
        df,
        x="committer_date",
        y=df["model-time"] / 1000000000,
        labels={
            "extractor": "Extractor",
            "y": "Time for Counting (log<sub>10</sub> s)",
            "committer_date": "Year",
        },
        hover_data=["revision"],
        log_y=True,
    )
    style_scatter(fig, legend_position=None, marker_size=2.5)
    show(
        fig,
        output_dir,
        f"model-count-time-{project}",
        plot_category="model-count-time",
        margin=dict(l=0, r=0, t=20, b=0),
    )


def model_count(df, project, output_dir):
    if df.dropna(subset=["model-literals"]).empty:
        print(
            f"'#Configurations' plot for project '{project}' could not be created because 'df[\"model-literals\"]' is empty.")
        return
    fig = px.scatter(
        df,
        x="committer_date",
        y="model-literals",
        labels={
            "extractor": "Extractor",
            "model-literals": "#Configurations",
            "committer_date": "Year",
        },
        hover_data=["revision"],
        log_y=True,
    )
    style_scatter(fig, legend_position=None, marker_size=2.5)
    show(
        fig,
        output_dir,
        f"model-count-{project}",
        plot_category="model-count",
        margin=dict(l=0, r=0, t=20, b=0),
    )


def sloc(df, project, output_dir):
    if df.dropna(subset=["source_lines_of_code"]).empty:
        print(
            f"'SLOC' plot for project '{project}' could not be created because 'df[\"source_lines_of_code\"]' is empty.")
        return
    fig = px.scatter(
        df[df["system"] == project],
        x="committer_date",
        y="source_lines_of_code",
        labels={
            "source_lines_of_code": "Number of Source Lines of Code",
            "committer_date": "Year",
        },
        hover_data=["revision"],
    )
    style_scatter(fig)
    show(fig, output_dir, f"source_lines_of_code-{project}", plot_category="source_lines_of_code")
