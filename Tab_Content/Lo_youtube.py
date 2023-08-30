import dash
from dash import html
from dash import dcc
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc

from Tab_Content.youtube_channel import youtube_channel_layout
from Tab_Content.youtube_comments import youtube_comments_lo

from app import app

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

youtube_LO = html.Div([

    html.H4(["Click on a tab: "], className=''),
    html.Li("Youtube Channel Metrics: This tab will show you the metrics like views, likes or comment count of videos uploaded from a youtube channel."),
    html.Li("YouTube ChatGPT Comments Analysis: This tab will show you the comments from a YouTube video. Using ChatGPT, users can determine the sentiment of the comments and can also generate 'Thank you' comments for the video."),

    html.Div([
        dcc.Tabs(id='youtube_tabs', value='',
                 children=[
                     dcc.Tab(
                         label='Youtube Channel Metrics',
                         value='channel',
                         style=tab_style,
                         selected_style=selected_tab_style,
                     ),

                     dcc.Tab(
                         label='Youtube ChatGPT Comments Analysis',
                         value='comments',
                         style=tab_style,
                         selected_style=selected_tab_style),

                 ], style=tabs_styles,
                 className='layout_tab_bar', colors={'border': None,
                                                     'primary': None,
                                                     'background': None})

    ], className='select_container'),


    html.Div(id='youtube_tab_content', className='analysis_content')


], className='LO_container')


@app.callback(Output('youtube_tab_content', 'children'),
              [Input('youtube_tabs', 'value')])
def update_youtube_tab_content(youtube_tabs):
    if youtube_tabs == 'channel':
        return youtube_channel_layout
    if youtube_tabs == 'comments':
        return youtube_comments_lo
