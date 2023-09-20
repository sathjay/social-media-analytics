import dash
from dash import html
from dash import dcc
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc

import pandas as pd
import numpy as np
import datetime

from app import app
from Tab_Content.home import home_LO
from Tab_Content.Lo_youtube import youtube_LO
from Tab_Content.Lo_reddit import reddit_lo
from Tab_Content.Lo_G_trends import google_trends_LO
from Tab_Content.about_me import about_me_LO


meta_tags = [{'name': 'viewport', 'content': 'width=device-width'}]
external_stylesheets = [meta_tags]


today = datetime.date.today()
year = today.year
copyright_message = f"© {year} -Sathya Jayagopi. All Rights Reserved."

server = app.server

tabs_styles = {'display': 'flex',
               'flex-direction': 'row',
               'margin-left': '10%',
               'margin-right': '10%',
               }

tab_style = {'color': 'grey',
             'border': 'none',
             'fontSize': '19px',
             'padding': '1.3vh',
             'padding-top': '1.5vh'
             }

selected_tab_style = {'color': 'blue',
                      'padding': '1.1vh',
                      'padding-top': '1.1vh',
                      'backgroundColor': '#f5f5f5ee',
                      'fontSize': '19px',
                      'border-top': '1px solid white',
                      'border-left': '1px solid white',
                      'border-right': '1px solid white',
                      'border-bottom': '3px solid red'}


app.layout = html.Div([

    html.Div([

        html.Div([
            html.Img(src=app.get_asset_url('Icon.png'), className='icon'),
            html.H1(['Social-Media Analytics with ChatGPT and NLP'],
                    className='title'),
        ], className='titleContainer'),

        html.Div([
            dcc.Tabs(id='main_tabs', value='home',
                 children=[
                     dcc.Tab(
                         label='Home',
                         value='home',
                         style=tab_style,
                         selected_style=selected_tab_style,
                     ),

                     dcc.Tab(label='Youtube',
                             value='Youtube',
                             style=tab_style,
                             selected_style=selected_tab_style),

                     dcc.Tab(label='Reddit',
                             value='Reddit',
                             style=tab_style,
                             selected_style=selected_tab_style,
                             ),

                     dcc.Tab(label='Google Trends',
                             value='google_trends',
                             style=tab_style,
                             selected_style=selected_tab_style),

                     dcc.Tab(label='About Me',
                             value='about_me',
                             style=tab_style,
                             selected_style=selected_tab_style),


                 ], style=tabs_styles,
                className='tab_bar', colors={'border': None,
                                             'primary': None,
                                             })

        ], className='tabCcontainer'),

    ], className='header'),


    html.Div(id='return_tab_content'),

    html.Footer([

        html.Div([html.P(copyright_message),

                  ], className='footerContent')

    ], className='footerContainer')



], className='mainContainer')


@app.callback(Output('return_tab_content', 'children'),
              [Input('main_tabs', 'value')])
def update_content(main_tabs):
    if main_tabs == 'home':
        return home_LO
    if main_tabs == 'Youtube':
        return youtube_LO
    if main_tabs == 'Reddit':
        return reddit_lo
    if main_tabs == 'google_trends':
        return google_trends_LO
    if main_tabs == 'about_me':
        return about_me_LO


if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080)
    # app.run_server(debug=True)
