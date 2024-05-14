import pandas as pd
import plotly.express as px
from dash import html, Dash, dcc, Input, Output, callback
import os

df = pd.read_csv("all_losses.csv")
app = Dash(__name__)

server = app.server

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
    html.H5(children="Loss type"),
    dcc.Dropdown(axis_options, "losses_total", id="bar-pie-y"),
    html.Div(children=[dcc.Graph("pie_ukraine")], style={"width": "48%", "display": "inline-block"}),
    html.Div(children=[dcc.Graph("pie_russia")], style={"width": "48%", "float": "right", "display": "inline-block"}),
    html.Div(children=[dcc.Graph("bar_ukraine")], style={"width": "48%", "display": "inline-block"}),
    html.Div(children=[dcc.Graph("bar_russia")], style={"width": "48%", "float": "right", "display": "inline-block"})
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
    filtered = df[df["equipment"].isin(selected_equipment)]
    filtered = filtered[filtered["model"].isin(selected_model)]
    filtered = filtered[filtered["manufacturer"].isin(selected_manufacturer)]
    bubble = px.scatter(filtered, x=x, y=y, size=size, color="lost_by", hover_name="model")
    bubble.update_layout(transition_duration=500)
    return bubble

@callback(Output("pie_ukraine", "figure"),
          Input("model", "value"),
          Input("equipment", "value"),
          Input("manufacturer", "value"),
          Input("bar-pie-y", "value"))
def update_pie_ukraine(selected_model, selected_equipment, selected_manufacturer, y):
    for item in [selected_equipment, selected_model, selected_manufacturer, y]:
        if item is None:
            return px.pie(df[df["lost_by"]=="ukraine"], values=y, names="manufacturer", title="Ukrainian losses by manufacturer")
    filtered = df[df["equipment"].isin(selected_equipment)]
    filtered = filtered[filtered["model"].isin(selected_model)]
    filtered = filtered[filtered["manufacturer"].isin(selected_manufacturer)]
    filtered = filtered[filtered["lost_by"]=="ukraine"]
    pie = px.pie(filtered, values=y, names="manufacturer", title="Ukrainian losses by manufacturer")
    pie.update_layout(transition_duration=500)
    return pie

@callback(Output("pie_russia", "figure"),
          Input("model", "value"),
          Input("equipment", "value"),
          Input("manufacturer", "value"),
          Input("bar-pie-y", "value"))
def update_pie_russia(selected_model, selected_equipment, selected_manufacturer, y):
    for item in [selected_equipment, selected_model, selected_manufacturer, y]:
        if item is None:
            return px.pie(df[df["lost_by"]=="russia"], values=y, names="manufacturer", title="Russian losses by manufacturer")
    filtered = df[df["equipment"].isin(selected_equipment)]
    filtered = filtered[filtered["model"].isin(selected_model)]
    filtered = filtered[filtered["manufacturer"].isin(selected_manufacturer)]
    filtered = filtered[filtered["lost_by"]=="russia"]
    pie = px.pie(filtered, values=y, names="manufacturer", title="Russian losses by manufacturer")
    pie.update_layout(transition_duration=500)
    return pie

@callback(Output("bar_ukraine", "figure"),
          Input("model", "value"),
          Input("equipment", "value"),
          Input("manufacturer", "value"),
          Input("bar-pie-y", "value"))
def update_bar_ukraine(selected_model, selected_equipment, selected_manufacturer, y):
    for item in [selected_equipment, selected_model, selected_manufacturer, y]:
        if item is None:
            return px.bar(df[df["lost_by"]=="ukraine"], x="model", y=y, title="Ukrainian losses by model")
    filtered = df[df["equipment"].isin(selected_equipment)]
    filtered = filtered[filtered["model"].isin(selected_model)]
    filtered = filtered[filtered["manufacturer"].isin(selected_manufacturer)]
    filtered = filtered[filtered["lost_by"]=="ukraine"]
    filtered = filtered[filtered[y]>0]
    bar = px.bar(filtered, x="model", y=y, title="Ukrainian losses by model")
    bar.update_layout(transition_duration=500)
    bar.update_xaxes(categoryorder="total ascending")
    return bar

@callback(Output("bar_russia", "figure"),
          Input("model", "value"),
          Input("equipment", "value"),
          Input("manufacturer", "value"),
          Input("bar-pie-y", "value"))
def update_bar_russia(selected_model, selected_equipment, selected_manufacturer, y):
    for item in [selected_equipment, selected_model, selected_manufacturer, y]:
        if item is None:
            return px.bar(df[df["lost_by"]=="russia"], x="model", y=y, title="Russian losses by model")
    filtered = df[df["equipment"].isin(selected_equipment)]
    filtered = filtered[filtered["model"].isin(selected_model)]
    filtered = filtered[filtered["manufacturer"].isin(selected_manufacturer)]
    filtered = filtered[filtered["lost_by"]=="russia"]
    filtered = filtered[filtered[y]>0]
    bar = px.bar(filtered, x="model", y=y, title="Russian losses by model")
    bar.update_layout(transition_duration=500)
    bar.update_xaxes(categoryorder="total ascending")
    return bar

if __name__ == "__main__":
    app.run(debug=True)
