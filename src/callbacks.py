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
            print("get trials...")
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
def set_current_color(current, trials):
    return (
        f"{current['id']}/{len(trials)} ({current['id'] / len(trials) * 100:.2f}%)"
        if current["id"]
        else ""
    )


@app.callback(
    output=Output("export-output", "children"),
    inputs=[Input("export", "n_clicks")],
    state=[State("trials", "data"), State("project", "value")],
)
def set_current_color(export, trials, project):
    out = "Export to csv"
    if trials:
        pd.DataFrame(trials).T.assign(
            trial=lambda x: x["filename"].str.split("/").str[-1]
        )[["filename", "trial", "tag", "note"]].to_csv(f"{project}/verification.csv")
        out = f"Export to csv (#{export})"
    return out
