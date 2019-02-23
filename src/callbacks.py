from pathlib import Path

import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State

from .server import app


@app.callback(
    output=Output("trials", "data"),
    inputs=[
        Input("read", "n_clicks_timestamp"),
        Input("tag-1", "n_clicks_timestamp"),
        Input("tag-2", "n_clicks_timestamp"),
        Input("tag-3", "n_clicks_timestamp"),
    ],
    state=[
        State("project", "value"),
        State("glob", "value"),
        State("trials", "data"),
        State("current", "data"),
    ],
)
def set_trials(read, t1, t2, t3, project, glob, trials, current):
    if read:
        btn = np.nanargmax(np.array([read, t1, t2, t3], dtype=np.float))
        if btn == 0:
            print("get trials...")
            out = {
                i: {"tag": 0, "filename": f"{itrial}"}
                for i, itrial in enumerate(Path(project).expanduser().glob(glob))
            }
        else:
            out = trials
            if btn == 1:
                out[f'{current["id"] - 1}']["tag"] = 1
            elif btn == 2:
                out[f'{current["id"] - 1}']["tag"] = 2
            elif btn == 3:
                out[f'{current["id"] - 1}']["tag"] = 3
    else:
        out = {}
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
    output=Output("progress", "children"),
    inputs=[Input("current", "data")],
    state=[State("trials", "data")],
)
def set_current_color(current, trials):
    return (
        f"{current['id']}/{len(trials)} ({current['id']/len(trials) * 100:.2f}%)"
        if current["id"]
        else ""
    )


@app.callback(
    output=Output("export-output", "children"),
    inputs=[Input("export", "n_clicks")],
    state=[State("trials", "data"), State("project", "value")],
)
def set_current_color(export, trials, project):
    if trials:
        pd.DataFrame(trials).T.to_csv(f"{project}/verification.csv")
    return export
