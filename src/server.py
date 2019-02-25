from dash import Dash

from .layout import *

# build app
external_stylesheets = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://cdn.rawgit.com/plotly/dash-app-stylesheets/"
    "2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",
]

rof = {
    # "thorax_tilt": [-90, 90], # clamped
    # "thorax_list": [-90, 90], # clamped
    # "thorax_rotation": [-90, 90], # clamped
    # "thorax_tx": [-20, 20], # clamped
    # "thorax_ty": [-2, 4], # clamped
    # "thorax_tz": [-5, 5], # clamped
    "sternoclavicular_r1": [-90, 90],
    "sternoclavicular_r2": [-90, 90],
    "Acromioclavicular_r1": [-90, 90],
    "Acromioclavicular_r2": [-90, 90],
    "Acromioclavicular_r3": [-90, 90],
    # "shoulder_plane": [-171.887, 20.053], # clamped
    # "shoulder_ele": [-17.189, 171.887], # clamped
    # "shoulder_rotation": [0, 171.887], # clamped
    "elbow_flexion": [0, 171.887],
    "pro_sup": [-90, 90],
    "hand_r_Add": [-68.755, 68.754],
    "hand_r_Flex": [-57.296, 57.295],
    "box_rotX": [-229.183, 229.183],
    "box_rotY": [-229.183, 229.183],
    "box_rotZ": [-229.183, 229.183],
    "box_transX": [-25, 25],
    "box_transY": [-25, 25],
    "box_transZ": [-25, 25],
}

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
        get_graph(),
    ]
)
