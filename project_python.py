"""this module contains the main functionality, design and callbacks of the dash app"""
import csv
import json
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from plotly.graph_objs import Scatter, Figure
import pandas as pd
import numpy as np

#from textwrap import dedent as d

from DataWrangling.wrangling import df_to_weight_df, calculate_weights, count_by_year
from DataWrangling.wrangling import get_data, clean_data, data_to_df_group
from Drawing.Graphs import draw_network_graph, draw_histogram


external_stylesheets = [
    # Dash CSS
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # Loading screen CSS
    'https://codepen.io/chriddyp/pen/brPBPO.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

colors = {
    'background': '#FFFFFF',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H3(
        children='Co-authorship of publications on WMiI UJ',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value0',
             style={'display': 'none'}),
    html.Div(id='intermediate-value',
             style={'display': 'none'}),

    html.Label('Please choose the unit of WMiI', style={
        'textAlign': 'left',
        'color': colors['text'],
        'padding': '0px 20px 0px 20px'
    }),
    html.Div(dcc.Dropdown(id='units-dropdown',
                          options=[
                              {'label': 'Whole WMiI',
                               'value': '1-wydzial-matematyki-i-informatyki-uj'},
                              {'label': 'Instytut informatyki i matematyki komputerowej',
                               'value': '2-instytut_informatyki_i_matematyki_komputerowej'},
                              {'label': 'Instytut Matematyki', 'value': '3-instytut_matematyki'},
                              {'label': 'Katedra Teorii Optymalizacji i Sterowania',
                               'value': '23-katedra_teorii_optymalizacji_i_sterowania'},
                              {'label': 'Zespół Katedr i Zakładów Informatyki Matematycznej',
                               'value': '4-zespol_katedr_i_zakladow_informatyki_matematycznej'},
                              {'label': 'Katedra Informatyki Stosowanej',
                               'value': '7-katedra_informatyki_stosowanej'},
                              {'label': 'Katedra Matematyki Obliczeniowej',
                               'value': '8-katedra_matematyki_obliczeniowej'},
                              {'label': 'Katedra Metod Efektywnych Algebry',
                               'value': '11-katedra_metod_efektywnych_algebry'},
                              {'label': 'Katedra Uczenia Maszynowego',
                               'value': '22-katedra_uczenia_maszynowego'},
                              {'label': 'Zakład Matematyki Dyskretnej',
                               'value': '10-zaklad_matematyki_dyskretnej'},
                              {'label': 'Katedra Analizy Funkcjonalnej',
                               'value': '12-katedra_analizy_funkcjonalnej'},
                              {'label': 'Katedra Analizy Matematycznej',
                               'value': '13-katedra_analizy_matematycznej'},
                              {'label': 'Katedra Funkcji Rzeczywistych',
                               'value': '14-katedra_funkcji_rzeczywistych'},
                              {'label': 'Katedra Geometrii', 'value': '16-katedra_geometrii'},
                              {'label': 'Katedra Geometrii Algebraicznej i Teorii Liczb',
                               'value': '24-katedra_geometrii_algebraicznej_i_teorii_liczb'},
                              {'label': 'Katedra Geometrii Analitycznej',
                               'value': '15-katedra_geometrii_analitycznej'},
                              {'label': 'Katedra Matematyki Stosowanej',
                               'value': '17-katedra_matematyki_stosowanej'},
                              {'label': 'Katedra Równań Różniczkowych',
                               'value': '18-katedra_rownan_rozniczkowych'},
                              {'label': 'Katedra Teorii Aproksymacji',
                               'value': '19-katedra_teorii_aproksymacji'},
                              {'label': 'Zakład Historii Matematyki',
                               'value': '20-zaklad_historii_matematyki'},
                              {'label': 'Zakład Matematyki Finansowej',
                               'value': '21-zaklad_matematyki_finansowej'},
                              {'label': 'Katedra Algorytmiki', 'value': '5-katedra_algorytmiki'},
                              {'label': 'Katedra Podstaw Informatyki',
                               'value': '6-katedra_podstaw_informatyki'}
                          ],
                          value='22-katedra_uczenia_maszynowego'),
             style={'padding': '0px 20px 0px 20px'}),

    html.Label('Filter by authors', style={
        'textAlign': 'left',
        'color': colors['text'],
        'padding': '0px 20px 0px 20px'
    }),

    dcc.Dropdown(id='authors-dropdown',
                 options=[{}],
                 # {'label': i, 'value': i} for i in authors],
                 value=[],
                 multi=True,
                 style={'padding': '0px 20px 0px 20px'}
                ),

    html.Div(dcc.Graph(id='network-graph'),
             style={"height": "100%", "width": "55%", 'display': 'inline-block',
                    'padding': '0px 0px 20px 0px'}),

    html.Div([
        dcc.Graph(id='publications-with-graph', style={'height': '300px'}),
        dcc.Graph(id='publications-years-graph', style={'height': '300px'}),
    ], style={'display': 'inline-block', 'width': '42%', 'height': '100%'}),

    html.Div(dcc.RangeSlider(
        id='year-range-slider',
        min=1969,
        max=2019,
        step=1,
        value=[1969, 2019],
        marks={str(value): str(value) for value in range(1969, 2020, 3)}
    ), style={'width': '55%', 'padding': '0px 20px 20px 20px'})
])


@app.callback(Output('intermediate-value', 'children'),
              [Input('units-dropdown', 'value')])
def save_data(value):
    """callback downloading data abouth publications of chosen unit,
    cleaning it and saving in an invisible div to be used later"""
    cleaned_list = clean_data(get_data(value))

    return json.dumps(cleaned_list)


@app.callback(Output('intermediate-value0', 'children'),
              [Input('intermediate-value', 'children')])
def save_final_data(jsonified_cleaned_list):
    """saving grouped data for optimization purposes"""
    cleaned_data = json.loads(jsonified_cleaned_list)
    dataframe = data_to_df_group(cleaned_data)

    return dataframe.to_json(date_format='iso', orient='split')


@app.callback(Output('authors-dropdown', 'options'),
              [Input('intermediate-value0', 'children')])
def update_dropdown(jsonified_cleaned_data):
    """callback updating the dropdown for filtering by author
    by names of authors from selected unit"""
    dataframe = pd.read_json(jsonified_cleaned_data, orient='split')
    names = np.unique(dataframe[['author', 'coauthor']].values)

    return [{'label': i, 'value': i} for i in names]


@app.callback(Output('network-graph', 'figure'),
              [Input('intermediate-value0', 'children'),
               Input('year-range-slider', 'value'),
               Input('authors-dropdown', 'value')],
              [State('intermediate-value', 'children')])
def show_network(jsonified_cleaned_data, years, authors, jsonified_cleaned_list):
    """callback showing the network graph of chosen unit"""
    dataframe = pd.read_json(jsonified_cleaned_data, orient='split')
    start_date, end_date = years[0], years[1]
    weights = {}
    cleaned_data = json.loads(jsonified_cleaned_list)
    weights = calculate_weights(cleaned_data, start_date, end_date)
    f_df = dataframe.loc[dataframe['year'].isin(range(start_date, end_date))]
    if authors:
        f_df = f_df[(f_df['author'].isin(authors)) | (f_df['coauthor'].isin(authors))]
    cleaned_df = df_to_weight_df(f_df)
    data, lay = draw_network_graph(cleaned_df, weights)
    fig = Figure(data=data, layout=lay)
    return fig


@app.callback(Output('publications-with-graph', 'figure'),
              [Input('network-graph', 'clickData')],
              [State('intermediate-value', 'children')])
def show_publications_graph(click_data, jsonified_cleaned_list):
    """callback showing the #of publications by year
     histogram of chosen author"""
    cleaned_data = json.loads(jsonified_cleaned_list)
    text = click_data['points'][0]['text']
    if ' has ' not in text:
        return {}
    else:
        words = text.split(" has ")
        name = words[0]
        years, counts = count_by_year(cleaned_data, name)
        title = '<br>#Publications by year <br> by {} and others'.format(name)
        figure = draw_histogram(years, counts, title)
        return figure


@app.callback(Output('publications-years-graph', 'figure'),
              [Input('network-graph', 'clickData'),
               Input('year-range-slider', 'value')],
              [State('intermediate-value0', 'children')])
def show_coauthors_graph(click_data, years, jsonified_cleaned_data):
    """callback showing the coauthors histogram of
    chosen author and optionally year"""
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    text = click_data['points'][0]['text']
    if ' has ' not in text:
        return {}
    else:
        words = text.split(" has ")
        name = words[0]
        start_date, end_date = years[0], years[1]
        filtered_df = df.loc[df['year'].isin(range(start_date, end_date))]
        filtered_df = filtered_df[(filtered_df.author == name) | (filtered_df.coauthor == name)]
        x, y = [], []
        for coauthor, val in filtered_df.author.value_counts().iteritems():
            if coauthor != name:
                x.append(coauthor)
                y.append(val)
        for coauthor, val in filtered_df.coauthor.value_counts().iteritems():
            if coauthor != name:
                x.append(coauthor)
                y.append(val)
        title = '<br>Coauthors of publications <br> by {}'.format(name)
        figure = draw_histogram(x, y, title)

        return figure


if __name__ == '__main__':
    app.run_server(debug=True)
