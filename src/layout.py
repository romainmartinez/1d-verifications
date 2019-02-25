import dash_core_components as dcc
import dash_html_components as html


def get_header():
    title = html.H1(
        "Time series verification",
        id="title",
        style={"margin-top": "25", "margin-bottom": "0"},
        className="six columns",
    )
    logo = html.Img(
        src="https://raw.github.com/pyomeca/design/master/logo/logo_plain.svg?sanitize=true",
        style={
            "height": "20%",
            "width": "20%",
            "float": "right",
            "position": "relative",
            "padding-top": 10,
            "padding-right": 0,
        },
        className="two columns",
    )
    return html.Div([title, logo], className="row")


def get_selection():
    style_div = {
        "margin-top": "5",
        "margin-bottom": "5",
        "margin-left": "5",
        "margin-right": "5",
    }
    button_style = {
        "font-family": "monospace",
        "font-size": 16,
        "color": "white",
        "background-color": "rgb(44,115,148)",
    }

    input_params = dict(
        placeholder="Enter a value...",
        type="text",
        size=25,
        style={"font-family": "monospace", "font-size": 18},
    )
    project = html.Div(
        [
            html.P("Project path"),
            dcc.Input(**input_params, id="project", value="~/Downloads/irsst"),
            dcc.Input(
                **input_params, id="glob", value="*/1_inverse_kinematic/*H2*.mot"
            ),
        ],
        className="three columns",
        style=style_div,
    )

    read = html.Div(
        [
            html.P("Read data"),
            html.Button("find", id="find", style=button_style),
            html.Button("read", id="read", style=button_style),
        ],
        className="one column",
        style=style_div,
    )

    column = html.Div(
        [
            html.P("Glob query"),
            dcc.Dropdown(
                id="columns",
                multi=True,
                value=[
                    "shoulder_ele",
                    "shoulder_rotation",
                    "elbow_flexion",
                    "hand_r_Flex",
                ],
            ),
        ],
        className="two columns",
        style=style_div,
    )

    controls = html.Div(
        [
            html.P("Controls", id="controls-output", style={"text-align": "center"}),
            html.Div(
                [html.Button("export", id="export", style=button_style)],
                style={"text-align": "center"},
            ),
            html.Div(
                [
                    html.Button(
                        "← [h]", id="previous", style=button_style, accessKey="h"
                    ),
                    html.Button("→ [j]", id="next", style=button_style, accessKey="j"),
                ],
                style={"text-align": "center"},
            ),
            html.Div(
                [
                    html.Button(
                        "1 [b]",
                        id="tag-1",
                        accessKey="b",
                        style={**button_style, **{"background-color": "#57bb8a"}},
                    ),
                    html.Button(
                        "2 [n]",
                        id="tag-2",
                        accessKey="n",
                        style={**button_style, **{"background-color": "#ffd666"}},
                    ),
                    html.Button(
                        "3 [m]",
                        id="tag-3",
                        accessKey="m",
                        style={**button_style, **{"background-color": "#e67c73"}},
                    ),
                ],
                style={"text-align": "center"},
            ),
        ],
        className="three columns",
        style=style_div,
    )

    current = html.Div(
        [
            html.P("Current trial"),
            html.P(
                "", id="progress", style={"font-family": "monospace", "font-size": 18}
            ),
            html.P(
                "          ",
                id="current-output",
                style={
                    "font-family": "monospace",
                    "font-size": 15,
                    "color": "white",
                    "background-color": "grey",
                    "text-align": "center",
                },
            ),
            dcc.Input(
                id="note", placeholder="Enter a note...", type="text", value="", size=25
            ),
        ],
        className="two columns",
        style={**style_div, **{"text-align": "center"}},
    )
    return html.Div([project, read, column, current, controls], className="row")


def get_graph():
    graph = dcc.Graph(id="lines", className="eight columns")
    warnings = dcc.Markdown("", id="warnings", className="three columns")
    return html.Div([graph, warnings], className="row")
