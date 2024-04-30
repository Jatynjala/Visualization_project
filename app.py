import pandas as pd
import plotly.express as px
from dash import html, Dash, dcc, Input, Output, callback

df = pd.read_csv("all_losses.csv")
app = Dash(__name__)

axis_options = df.columns.to_list()[5:16]

app.layout = html.Div([
    html.H1(children="Visualization of visually confirmed russo-ukrainian equipment losses in 2022"),
    html.Hr(),
    html.H3(children="More information"),
    dcc.Link(children="Based on this dataset", href="https://www.kaggle.com/datasets/piterfm/2022-ukraine-russia-war-equipment-losses-oryx?select=losses_ukraine.csv"),
    html.Br(),
    dcc.Link(children="Github page", href="https://github.com/Jatynjala/Visualization_project"),
    html.Hr(),
    html.H3(children="Select a subset of data"),
    html.H5(children="Equipment type"),
    dcc.Dropdown(df["equipment"].unique().tolist(), multi=True, id="equipment"),
    html.H5(children="Equipment manufacturer"),
    dcc.Dropdown(multi=True, id="manufacturer"),
    html.H5(children="Equipment model"),
    dcc.Dropdown(multi=True, id="model"),
    html.Hr(),
    html.H3(children="Bubble chart"),
    html.Div(children=[
        html.H5(children="x-axis"),
        dcc.Dropdown(axis_options, "losses_total", id="bubble-x"),
        html.H5(children="y-axis"),
        dcc.Dropdown(axis_options, "destroyed", id="bubble-y"),
        html.H5(children="bubble size"),
        dcc.Dropdown(axis_options, "captured", id="bubble-size")
        ], style={"width": "20%", "float": "right", "display": "inline-block"}),
    html.Div(children=[dcc.Graph("bubble")], style={"width": "75%", "display": "inline-block"}),
    html.Hr(),
    html.H3(children="Bar and pie charts"),
    html.Div(children=[dcc.Graph("pie")], style={"width": "75%", "display": "inline-block"}),
    html.Div(children=[
        html.H5(children="Loss type"),
        dcc.Dropdown(axis_options, "losses_total", id="bar-pie-y")
        ], style={"width": "20%", "float": "right", "display": "inline-block"}),
    dcc.Graph("bar")
    ])

@callback(Output("manufacturer", "options"), Input("equipment", "value"))
def set_manufacturer_options(selected_equipment):
    if selected_equipment is None:
        return []
    filtered = df[df["equipment"].isin(selected_equipment)]
    return filtered["manufacturer"].unique().tolist()

@callback(Output("manufacturer", "value"), Input("manufacturer", "options"))
def set_manufacturer_value(manufacturer_options):
    return manufacturer_options

@callback(Output("model", "options"), Input("equipment", "value"), Input("manufacturer", "value"))
def set_model_options(selected_equipment, selected_manufacturer):
    if selected_equipment is None:
        return []
    filtered = df[df["equipment"].isin(selected_equipment)]
    if selected_manufacturer is None:
        return filtered["model"].unique().tolist()
    filtered = filtered[filtered["manufacturer"].isin(selected_manufacturer)]
    return filtered["model"].unique().tolist()

@callback(Output("model", "value"), Input("model", "options"))
def set_model_value(model_options):
    return model_options

@callback(Output("bubble", "figure"),
          Input("model", "value"),
          Input("equipment", "value"),
          Input("manufacturer", "value"),
          Input("bubble-x", "value"),
          Input("bubble-y", "value"),
          Input("bubble-size", "value"))
def update_bubble(selected_model, selected_equipment, selected_manufacturer, x, y, size):
    for item in [selected_equipment, selected_model, selected_manufacturer, x, y, size]:
        if item is None:
            return px.scatter(df, x=x, y=y, size=size, color="lost_by")
    #print([x, y, size])
    filtered = df[df["equipment"].isin(selected_equipment)]
    filtered = filtered[filtered["model"].isin(selected_model)]
    filtered = filtered[filtered["manufacturer"].isin(selected_manufacturer)]
    bubble = px.scatter(filtered, x=x, y=y, size=size, color="lost_by", hover_name="model")
    bubble.update_layout(transition_duration=500)
    return bubble

@callback(Output("pie", "figure"),
          Input("model", "value"),
          Input("equipment", "value"),
          Input("manufacturer", "value"),
          Input("bar-pie-y", "value"))
def update_pie(selected_model, selected_equipment, selected_manufacturer, y):
    for item in [selected_equipment, selected_model, selected_manufacturer, y]:
        if item is None:
            return px.pie(df, values=y, names="manufacturer", title="Losses by manufacturer")
    filtered = df[df["equipment"].isin(selected_equipment)]
    filtered = filtered[filtered["model"].isin(selected_model)]
    filtered = filtered[filtered["manufacturer"].isin(selected_manufacturer)]
    pie = px.pie(filtered, values=y, names="manufacturer", title="Losses by manufacturer")
    pie.update_layout(transition_duration=500)
    return pie

@callback(Output("bar", "figure"),
          Input("model", "value"),
          Input("equipment", "value"),
          Input("manufacturer", "value"),
          Input("bar-pie-y", "value"))
def update_bar(selected_model, selected_equipment, selected_manufacturer, y):
    for item in [selected_equipment, selected_model, selected_manufacturer, y]:
        if item is None:
            return px.bar(df, x="model", y=y, title="Losses by model")
    filtered = df[df["equipment"].isin(selected_equipment)]
    filtered = filtered[filtered["model"].isin(selected_model)]
    filtered = filtered[filtered["manufacturer"].isin(selected_manufacturer)]
    filtered = filtered[filtered[y]>0]
    bar = px.bar(filtered, x="model", y=y, color="lost_by", title="Losses by model")
    bar.update_layout(transition_duration=500)
    return bar

if __name__ == "__main__":
    app.run(debug=True)
