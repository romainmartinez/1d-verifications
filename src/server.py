from dash import Dash

from .layout import *


# build app
external_stylesheets = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://cdn.rawgit.com/plotly/dash-app-stylesheets/"
    "2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# set layout
app.layout = html.Div(
    [
        dcc.Store(id="trials", data={}),
        dcc.Store(id="df", data={}),
        dcc.Store(id="current", data={"id": 0}),
        get_header(),
        get_selection(),
        dcc.Graph(id="lines"),
    ]
)
