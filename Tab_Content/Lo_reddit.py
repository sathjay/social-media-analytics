import dash
from dash import html
from dash import dcc
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc

from Tab_Content.reddit_chatgpt import reddit_chatgpt_lo
from Tab_Content.reddit_textblob import reddit_text_blob_lo

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

reddit_lo = html.Div([

    html.H4(["Click on a tab below: "], className='layout_title'),
    html.Li("Reddit Title Analysis: Under this tab, users can analyze post titles from popular subreddit handles using Natural Language Processing (NLP) to determine the sentiment of the title."),
    html.Li("Reddit ChatGPT Post Analysis: Under this tab, users can use ChatGPT to summarize articles or posts pertaining to the field of finance and investing, and determine the sentiment of the post (Bullish, Bearish, or Neutral)."),

    html.Div([
        dcc.Tabs(id='reddit_tabs', value='',
                 children=[
                     dcc.Tab(
                         label='Reddit Title Analysis',
                         value='reddit_textblob',
                         style=tab_style,
                         selected_style=selected_tab_style,
                     ),

                     dcc.Tab(
                         label='Reddit ChatGPT Post Analysis',
                         value='reddit_chatgpt',
                         style=tab_style,
                         selected_style=selected_tab_style),

                 ], style=tabs_styles,
                 className='layout_tab_bar', colors={'border': None,
                                                     'primary': None,
                                                     'background': None})

    ], className='select_container'),

    html.Div(id='reddit_tab_content', className='analysis_content')


], className='LO_container')


@app.callback(Output('reddit_tab_content', 'children'),
              [Input('reddit_tabs', 'value')])
def update_youtube_tab_content(reddit_tabs):
    if reddit_tabs == 'reddit_textblob':
        return reddit_text_blob_lo
    if reddit_tabs == 'reddit_chatgpt':
        return reddit_chatgpt_lo
