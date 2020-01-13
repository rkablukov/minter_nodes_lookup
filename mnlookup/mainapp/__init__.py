import os
from dash import Dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from .database import (load_nodes, load_countries, load_stat, 
                       load_ases, random_api_node, load_history)

TITLE = "Minter Nodes Lookup"
FLUID = False
MAPBOX_ACCESS_TOKEN = os.environ.get('MAPBOX_ACCESS_TOKEN', False)
if not MAPBOX_ACCESS_TOKEN:
    raise Exception("MAPBOX_ACCESS_TOKEN has not been defined.")


def navbar():
    """
    Функция возвращает меню приложения
    """
    navbar = dbc.NavbarSimple(
        children=[
            #dbc.NavItem(dbc.NavLink("Link", href="#")),
            #dbc.DropdownMenu(
            #    nav=True,
            #    in_navbar=True,
            #    label='Applications',
            #    children=[
            #        dbc.DropdownMenuItem("Entry 1"),
            #        dbc.DropdownMenuItem("Entry 2"),
            #        dbc.DropdownMenuItem(divider=True),
            #        dbc.DropdownMenuItem("Entry 3"),
            #    ],
            #),
        ],
        brand=TITLE,
        brand_href="#",
        #sticky="top",
        fluid=FLUID
    )
    return navbar


def nodes_stat():
    n_nodes, n_api, n_full_nodes = load_stat()
    api_node = random_api_node()

    stat_block = dbc.Container(
        dbc.Row([
            dbc.Col(
                html.Div([html.Small("Nodes"), html.Br(), html.Span(n_nodes)]), 
                width=3,
                xs=4,
                lg=3
            ),
            dbc.Col(
                html.Div([html.Small("Api Nodes"), html.Br(), html.Span(n_api)]), 
                width=3,
                xs=4,
                lg=3
            ),
            dbc.Col(
                html.Div([html.Small("Full Api Nodes"), html.Br(), html.Span(n_full_nodes)]), 
                width=3,
                xs=4,
                lg=3
            ),
            dbc.Col(
                html.Div([html.Small("Random Api Node Url"), html.Br(), html.Span(html.A(api_node, href=api_node))]), 
                width=3,
                xs=12,
                lg=3
            ),
        ]),
        fluid=FLUID,
        className='mt-4 mb-4'
    )
    return stat_block


def map_block():
    text, lat, lon = load_nodes()

    fig_map = go.Figure(go.Scattermapbox(
        lat=lat,
        lon=lon,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=9
        ),
        text=text,
    ))

    fig_map.update_layout(
        autosize=True,
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken=MAPBOX_ACCESS_TOKEN,
            bearing=0,
            center=go.layout.mapbox.Center(
                #lat=53.3498,
                #lon=-6.26031
                #lat=(min(lat)+max(lat))/2,
                #lon=(min(lon)+max(lon))/2
                lat=sum(lat)/len(lat),
                lon=sum(lon)/len(lon)
            ),
            pitch=0,
            zoom=2
        ),
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
    )

    map_card = dbc.Container(
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dcc.Graph(
                        id='nodes-map',
                        figure=fig_map
                    )
                ),
                width=12
            )
        ),
        fluid=FLUID
    )
    return map_card


def countries_chart():
    countries, number_of_nodes = load_countries()

    fig_countries = go.Figure([go.Bar(y=countries, x=number_of_nodes, orientation='h')])
    fig_countries.update_layout(
        yaxis=dict(autorange="reversed"),
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        xaxis={'side': 'top', 'fixedrange': True},
        height=300,
        plot_bgcolor='rgb(255,255,255)'
    )

    countries_card = [
        html.H5("Countries"),
        html.Div(
            dcc.Graph(
                id='countries-bar',
                figure=fig_countries,
                config={'displayModeBar': False}
            )
        )
    ]
    return countries_card


def ases_chart():
    ases, number_of_nodes = load_ases()

    _fig = go.Figure([go.Bar(y=ases, x=number_of_nodes, orientation='h')])
    _fig.update_layout(
        yaxis=dict(autorange="reversed"),
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        xaxis={'side': 'top', 'fixedrange': True},
        height=300,
        plot_bgcolor='rgb(255,255,255)'
    )

    _card = [
        html.H5("Autonomous Systems"),
        html.Div(
            dcc.Graph(
                id='ases-bar',
                figure=_fig,
                config={'displayModeBar': False}
            )
        )
    ]
    return _card


def history_chart():
    dates, nodes = load_history()

    _fig = go.Figure(data=go.Scatter(x=dates, y=nodes))
    _fig.update_layout(
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        xaxis={'fixedrange': True},
        height=300,
        plot_bgcolor='rgb(255,255,255)'
    )

    _card = [
        html.H5("Number of nodes"),
        html.Div(
            dcc.Graph(
                id='nodes-line',
                figure=_fig,
                config={'displayModeBar': False}
            )
        )
    ]
    return _card    


def main_app():
    dash_app = Dash(
        __name__,
        server=False,
        url_base_pathname='/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        meta_tags=[
            #{'name':'viewport','content':'width=device-width, user-scalable=no'}
            #{'name':'viewport','content':'width=device-width, initial-scale=0.85'},
            {'name': 'viewport',
             'content': 'width=device-width, initial-scale=1'},
        ]
    )

    dash_app.title = TITLE

    dash_app.layout = html.Div([
        navbar(), 
        nodes_stat(),
        map_block(),
        dbc.Container(
            dbc.Row([
                dbc.Col(
                    countries_chart(),
                    width=4,
                    xs=12,
                    md=6,
                    lg=4,
                    className='mt-4'
                ),
                dbc.Col(
                    ases_chart(),
                    width=4,
                    xs=12,
                    md=6,
                    lg=4,
                    className='mt-4'
                ),
                dbc.Col(
                    history_chart(),
                    width=4,
                    xs=12,
                    lg=4,
                    className='mt-4'
                )
            ]),
            fluid=FLUID,
            className='mb-4'
        ),
        html.Footer(
            dbc.Container(
                dbc.Row(
                    dbc.Col(
                        html.Small("Roman Kablukov © 2020")
                    )
                )
            ),
            className="p-3 mb-2 bg-light text-dark"
        )
    ])

    return dash_app
