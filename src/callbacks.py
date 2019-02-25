import time
from pathlib import Path

import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from plotly import tools
from pyosim import Analogs3dOsim

from .server import app, rof


@app.callback(
    output=Output("trials", "data"),
    inputs=[
        Input("find", "n_clicks_timestamp"),
        Input("tag-1", "n_clicks_timestamp"),
        Input("tag-2", "n_clicks_timestamp"),
        Input("tag-3", "n_clicks_timestamp"),
        Input("note", "n_submit_timestamp"),
    ],
    state=[
        State("project", "value"),
        State("glob", "value"),
        State("trials", "data"),
        State("current", "data"),
        State("note", "value"),
    ],
)
def set_trials(read, t1, t2, t3, note_submit, project, glob, trials, current, note):
    if read:
        note_submit = pd.to_datetime(note_submit).timestamp() if note_submit else None
        read = pd.to_datetime(read, unit="ms").timestamp() if read else None
        t1 = pd.to_datetime(t1, unit="ms").timestamp() if t1 else None
        t2 = pd.to_datetime(t2, unit="ms").timestamp() if t2 else None
        t3 = pd.to_datetime(t3, unit="ms").timestamp() if t3 else None
        btn = np.nanargmax(np.array([read, t1, t2, t3, note_submit], dtype=np.float))
        if btn == 0:
            print("finding trials...")
            out = {
                i: {"filename": f"{itrial}", "tag": 0, "note": ""}
                for i, itrial in enumerate(Path(project).expanduser().glob(glob))
            }
        else:
            out = trials
            if btn == 1:
                print("set to 1...")
                out[f'{current["id"] - 1}']["tag"] = 1
            elif btn == 2:
                print("set to 2...")
                out[f'{current["id"] - 1}']["tag"] = 2
            elif btn == 3:
                print("set to 3...")
                out[f'{current["id"] - 1}']["tag"] = 3
            elif btn == 4:
                print("set note...")
                out[f'{current["id"] - 1}']["note"] = note
    else:
        out = {}
    return out


@app.callback(
    output=Output("df", "data"),
    inputs=[Input("read", "n_clicks_timestamp")],
    state=[State("trials", "data")],
)
def read_data(_, trials):
    out = {}
    if trials:
        print("reading files...")
        ext = trials["1"]["filename"].split(".")[-1]
        d = (
            pd.concat(
                [
                    getattr(Analogs3dOsim, f"from_{ext}")(trials[i]["filename"])
                    .time_normalization()
                    .update_misc({"filename": trials[i]["filename"].split("/")[-1]})
                    .to_dataframe(add_metadata=["misc"])
                    for i in trials
                ]
            )
            .assign(filename=lambda x: x["filename"].astype("category"))
            .reset_index()
        )
        out = {
            "mean": d.groupby("index").mean().to_json(),
            "std": d.groupby("index").std().to_json(),
        }
    return out


@app.callback(output=Output("columns", "options"), inputs=[Input("df", "data")])
def set_dropdown_options(df):
    out = (
        [{"label": i, "value": i} for i in pd.read_json(df["mean"])]
        if df
        else [{"label": "", "value": ""}]
    )
    return out


def read_trials_and_current(df, trials, current):
    mu = pd.read_json(df["mean"]).sort_index()
    sigma = pd.read_json(df["std"]).sort_index()
    ext = trials["1"]["filename"].split(".")[-1]

    current_data = (
        getattr(Analogs3dOsim, f"from_{ext}")(
            trials[f'{current["id"] - 1}']["filename"]
        )
        .time_normalization()
        .to_dataframe()
    )
    return mu, sigma, current_data


@app.callback(
    output=Output("warnings", "children"),
    inputs=[Input("current", "data"), Input("columns", "value")],
    state=[State("df", "data"), State("trials", "data")],
)
def make_warnings(
    current, columns, df, trials, std_threshold=15, rof_threshold=5, rof=rof
):
    out = ["#### Warnings", "##### Outliers"]
    if df and columns and current and current["id"] > 0:
        mu, sigma, current_data = read_trials_and_current(df, trials, current)

        above = (current_data > mu + 3 * sigma).sum() / mu.shape[0] * 100
        below = (current_data < mu - 3 * sigma).sum() / mu.shape[0] * 100

        out.extend(
            [
                f"- `{icol}` > 3 std for __`{ival:.2f}%`__"
                for icol, ival in above.loc[above > std_threshold].iteritems()
            ]
        )
        out.extend(
            [
                f"- `{icol}` < 3 std for __`{ival:.2f}%`__"
                for icol, ival in below.loc[below > std_threshold].iteritems()
            ]
        )
        if rof:
            out.extend(["---", "##### Limits reach"])
            r = pd.DataFrame(rof, index=["lower", "upper"])
            rof_above = (current_data > r.loc["upper"] - 1).sum() / mu.shape[0] * 100
            rof_below = (current_data < r.loc["lower"] + 1).sum() / mu.shape[0] * 100
            out.extend(
                [
                    f"> - `{icol}` reaches upper DoF limit for __`{ival:.2f}%`__"
                    for icol, ival in rof_above.loc[
                        rof_above > rof_threshold
                    ].iteritems()
                ]
            )
            out.extend(
                [
                    f"> - `{icol}` reaches lower DoF limit for __`{ival:.2f}%`__"
                    for icol, ival in rof_below.loc[
                        rof_below > rof_threshold
                    ].iteritems()
                ]
            )
    return out


@app.callback(
    output=Output("lines", "figure"),
    inputs=[Input("current", "data"), Input("columns", "value")],
    state=[State("df", "data"), State("trials", "data")],
)
def make_lines(current, columns, df, trials):
    out = dict(data=[], layout={})
    if df and columns and current and current["id"] > 0:
        mu, sigma, current_data = read_trials_and_current(df, trials, current)
        out = tools.make_subplots(
            rows=2, cols=2, print_grid=False, shared_xaxes=True, shared_yaxes=True
        )
        pos = {0: [1, 1], 1: [1, 2], 2: [2, 1], 3: [2, 2]}
        for i, icol in enumerate(columns):
            # lower
            out.append_trace(
                go.Scatter(
                    x=mu.index,
                    y=mu[icol] - sigma[icol],
                    marker=dict(color="#444"),
                    line=dict(width=0),
                    mode="lines",
                ),
                row=pos[i][0],
                col=pos[i][1],
            )
            # trace
            out.append_trace(
                go.Scatter(
                    x=mu.index,
                    y=mu[icol],
                    mode="lines",
                    line=dict(color="black"),
                    fillcolor="rgba(68, 68, 68, 0.3)",
                    fill="tonexty",
                ),
                row=pos[i][0],
                col=pos[i][1],
            )
            # upper
            out.append_trace(
                go.Scatter(
                    x=mu.index,
                    y=mu[icol] + sigma[icol],
                    mode="lines",
                    marker=dict(color="#444"),
                    line=dict(width=0),
                    fillcolor="rgba(68, 68, 68, 0.3)",
                    fill="tonexty",
                ),
                row=pos[i][0],
                col=pos[i][1],
            )
            # current trial
            out.append_trace(
                go.Scatter(
                    x=current_data.index,
                    y=current_data[icol],
                    mode="lines",
                    line=dict(color="rgb(44,115,148)"),
                ),
                row=pos[i][0],
                col=pos[i][1],
            )
        out.layout.update(dict(showlegend=False, margin=dict(l=30, r=30, b=30, t=30)))
    return out


@app.callback(
    output=Output("current", "data"),
    inputs=[
        Input("previous", "n_clicks_timestamp"),
        Input("next", "n_clicks_timestamp"),
    ],
    state=[State("current", "data")],
)
def trial_navigation(prvs, nxt, current):
    incr = 0
    if nxt and not prvs:
        incr = 1
    elif prvs and not nxt:
        incr = -1
    elif nxt and prvs:
        if nxt > prvs:
            incr = 1
        else:
            incr = -1
    c = current["id"] + incr
    return {"id": c if c > -1 else 0}


@app.callback(
    output=Output("current-output", "children"),
    inputs=[Input("current", "data")],
    state=[State("trials", "data")],
)
def set_current_text(current, trials):
    return (
        Path(trials[f'{current["id"] - 1}']["filename"]).stem if current["id"] else ""
    )


@app.callback(
    output=Output("current-output", "style"),
    inputs=[Input("current", "data"), Input("trials", "data")],
)
def set_current_color(current, trials):
    color = "gray"
    if current["id"]:
        tag = trials[f'{current["id"] - 1}']["tag"]
        if tag == 1:
            color = "#57bb8a"
        elif tag == 2:
            color = "#ffd666"
        elif tag == 3:
            color = "#e67c73"
    return {
        "font-family": "monospace",
        "font-size": 18,
        "color": "white",
        "background-color": color,
        "text-align": "center",
    }


@app.callback(
    output=Output("note", "value"),
    inputs=[Input("current", "data")],
    state=[State("trials", "data")],
)
def set_note(current, trials):
    return trials[f'{current["id"] - 1}']["note"] if current["id"] else ""


@app.callback(
    output=Output("progress", "children"),
    inputs=[Input("current", "data")],
    state=[State("trials", "data")],
)
def set_progression(current, trials):
    return (
        f"{current['id']}/{len(trials)} ({current['id'] / len(trials) * 100:.2f}%)"
        if current["id"]
        else ""
    )


@app.callback(
    output=Output("controls-output", "children"),
    inputs=[Input("export", "n_clicks")],
    state=[State("trials", "data"), State("project", "value")],
)
def export_csv(_, trials, project):
    if trials:
        pd.DataFrame(trials).T.assign(
            trial=lambda x: x["filename"].str.split("/").str[-1]
        )[["filename", "trial", "tag", "note"]].to_csv(f"{project}/verification.csv")
    return "Controls"
