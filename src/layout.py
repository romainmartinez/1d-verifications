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
        "margin-top": "10",
        "margin-bottom": "10",
        "margin-left": "10",
        "margin-right": "10",
    }
    button_style = {
        "font-family": "monospace",
        "font-size": 18,
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
        ],
        className="two columns",
        style=style_div,
    )
    glob = html.Div(
        [
            html.P("Glob query"),
            dcc.Input(**input_params, id="glob", value="*/0_markers/*H2*.trc"),
        ],
        className="two columns",
        style=style_div,
    )
    read = html.Div(
        [html.P("Read data"), html.Button("read", id="read", style=button_style)],
        className="one column",
        style=style_div,
    )

    controls = html.Div(
        [
            html.P("Controls", style={"text-align": "center"}),
            html.Div(
                [
                    html.Button("←", id="previous", style=button_style),
                    html.Button("→", id="next", style=button_style),
                ],
                style={"text-align": "center"},
            ),
            html.Div(
                [
                    html.Button(
                        "1",
                        id="tag-1",
                        style={**button_style, **{"background-color": "#57bb8a"}},
                    ),
                    html.Button(
                        "2",
                        id="tag-2",
                        style={**button_style, **{"background-color": "#ffd666"}},
                    ),
                    html.Button(
                        "3",
                        id="tag-3",
                        style={**button_style, **{"background-color": "#e67c73"}},
                    ),
                ],
                style={"text-align": "center"},
            ),
        ],
        className="two columns",
        style=style_div,
    )

    current = html.Div(
        [
            html.P("Current trial"),
            html.P(
                "          ",
                id="current-output",
                style={
                    "font-family": "monospace",
                    "font-size": 18,
                    "color": "white",
                    "background-color": "grey",
                    "text-align": "center",
                },
            ),
            dcc.Input(
                id="note", placeholder="Enter a note...", type="text", value="", size=10
            ),
        ],
        className="one third columns",
        style=style_div,
    )

    progress = html.Div(
        [
            html.P("Progress"),
            html.P(
                "23/120 (14%)",
                id="progress",
                style={"font-family": "monospace", "font-size": 18},
            ),
        ],
        className="two columns",
        style=style_div,
    )

    export = html.Div(
        [
            html.P("Export to csv", id="export-output"),
            html.Button("export", id="export", style=button_style),
        ],
        className="one column",
        style=style_div,
    )

    return html.Div(
        [project, glob, read, controls, current, progress, export], className="row"
    )
