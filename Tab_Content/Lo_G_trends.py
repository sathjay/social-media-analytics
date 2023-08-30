import dash
from dash import html
from dash import dcc
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
from app import app

from Tab_Content.g_trending_today import g_trend_today_lo
from Tab_Content.g_top_trends_in_given_year import g_top_trends_in_given_year_lo
from Tab_Content.g_interest_by_region import g_interest_by_region_lo
from Tab_Content.g_interest_over_time import g_interest_over_time_lo


tabs_styles = {'display': 'flex',
               'flex-direction': 'row',
               'margin-left': '10%',
               'margin-right': '10%',
               }

tab_style = {'color': 'grey',
             'border': 'none',
             'fontSize': '19px',
             'fontWeight': 550,
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

google_trends_LO = html.Div([

    html.H4(["Click on a tab below: "], className='layout_title'),
    html.Li("Trending Today: This tab will show you the top 15 trending searches on Google today."),
    html.Li("Top Trends in Given year: This tab will show you the top 10 trending searches on Google in a given year."),
    html.Li("Popularity Country-wise: This tab will show you the relative popularity of a given topic/term country-wise."),
    html.Li("Trends over Time: This tab will display the relative popularity of a given topic/term across different countries and over time."),
    html.P(["(Note: The data is sourced from Pytrends API and is not an official Google Trends API. Since it is not an official API, chances of request time out or no response from server are quite high. If you encounter any such error, please try again after some time.)"], className='note'),

    html.Div([
        dcc.Tabs(id='gtrends_tabs', value='',
                 children=[
                    dcc.Tab(
                        label='Trending Today',
                        value='tt',
                        style=tab_style,
                        selected_style=selected_tab_style,),

                    dcc.Tab(
                        label='Top Trends in Given year',
                        value='tgy',
                        style=tab_style,
                        selected_style=selected_tab_style),

                    dcc.Tab(
                        label='Popularity Country-wise',
                        value='ibr',
                        style=tab_style,
                        selected_style=selected_tab_style),

                    dcc.Tab(
                        label='Trends over Time',
                        value='iot',
                        style=tab_style,
                        selected_style=selected_tab_style),

                 ], style=tabs_styles,
                 className='layout_tab_bar', colors={'border': None,
                                                     'primary': None,
                                                     'background': None})

    ], className='select_container'),


    html.Div(id='g_trends_tab_content', className='analysis_content')


], className='LO_container')


@app.callback(Output('g_trends_tab_content', 'children'),
              [Input('gtrends_tabs', 'value')])
def update_youtube_tab_content(gtrends_tabs):
    if gtrends_tabs == 'tt':
        return g_trend_today_lo
    if gtrends_tabs == 'tgy':
        return g_top_trends_in_given_year_lo
    if gtrends_tabs == 'ibr':
        return g_interest_by_region_lo
    if gtrends_tabs == 'iot':
        return g_interest_over_time_lo
