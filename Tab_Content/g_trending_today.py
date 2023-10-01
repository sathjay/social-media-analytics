import pandas as pd
import numpy as np
# Plotly Graphing Libraries
import plotly
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

from pytrends.request import TrendReq
from app import app

country_code_df = pd.read_csv(
    './assets/ISO_Country_Codes.csv', index_col='name')

country_drop_down_list = []
for i in range(0, len(country_code_df)):
    country_drop_down_list.append({'label': country_code_df.index[i],
                                   'value': country_code_df['alpha-2'][i]})


g_trend_today_lo = html.Div([
    html.H5("Google Trends: Trending Searches Today"),
    html.Div([
        html.Label(["Select a Country from the dorp down to see what's trending there:"],
                   className='label'),
        html.Br(),
        dcc.Dropdown(id='country_code_tt',
                     options=country_drop_down_list,
                     optionHeight=35,
                     disabled=False,  # disable dropdown value selection
                     multi=False,  # allow multiple dropdown values to be selected
                     searchable=True,  # allow user-searching of dropdown values
                     value='IE',
                     # placeholder='Select Country',  # gray, default text shown when no option is selected
                     clearable=True,  # allow user to removes the selected value
                     className='dropdown_box',  # activate separate CSS document in assets folder
                     ),
    ], className='g_selection'),
    html.Br(),
    html.Button('Submit', id='submit_ctry_tt', className='button', n_clicks=0),
    html.Br(),
    html.Div(id='trending_tt_summary'),
    html.Br(),
    html.Div([
        dash_table.DataTable(id='trending_tt',
                             cell_selectable=False,
                             style_header={
                                'backgroundColor': 'rgb(62, 152, 211)',
                                 'fontSize': '18px',
                                 'fontWeight': 'bold',
                                 'textAlign': 'center',
                                 'color': 'white',
                                 'height': 'auto',
                                 'lineHeight': '15px', },
                             style_cell={
                                'fontSize': '14px'},
                             style_cell_conditional=[
                                 {
                                     'if': {'column_id': 'Rank'},
                                     'width': '16px',
                                     'textAlign': 'center'},
                                 {
                                     'if': {'column_id': 'Search Topics'},
                                     'maxWidth': '750px',
                                                 'textAlign': 'left',
                                                 'textOverflow': 'ellipsis',
                                                 'padding-left': '8px', },],

                             ),
    ], className='small_table'),

])


@app.callback(
    [
        Output('trending_tt_summary', 'children'),
        Output('trending_tt', component_property='data'),
        Output('trending_tt', component_property='columns')],
    [Input('submit_ctry_tt', 'n_clicks')],
    [State('country_code_tt', 'value')],
    prevent_initial_call=True
)
def update_trending_search_now(n_clicks, country_code_tt):

    ctry_cd = country_code_tt
    tt_data = []
    tt_columns = []

    if ctry_cd == None:
        trending_tt_summary = 'Please select a country from the drop down to see what\'s trending there.'

        trending_tt_summary_div = html.Div([
            html.Div([], className='content_separator'),  # separator line
            html.H5([trending_tt_summary], className='content_message', style={'fontWeight': 500}),])

        return trending_tt_summary_div, tt_data, tt_columns

    try:
        pytrends = TrendReq()
        df = pytrends.realtime_trending_searches(pn=ctry_cd)
        df = df[['title']]

        df["Rank"] = np.arange(1, len(df) + 1)
        rank_column = df.pop('Rank')
        df.insert(0, 'Rank', rank_column)

        df.rename(columns={'title': 'Search Topics'}, inplace=True)

        df = df[0:15]  # Only first 15 results are displayed.

        tt_columns = [{'name': col, 'id': col} for col in df.columns]
        tt_data = df.to_dict(orient='records')

        country_name = country_code_df.loc[country_code_df['alpha-2']
                                           == ctry_cd].index.values[0]

        trending_tt_summary = 'The current top 15 trending search topics in {} are:'.format(
            country_name)

        trending_tt_summary_div = html.Div([
            html.Div([], className='content_separator'),  # separator line
            html.H5([trending_tt_summary], className='content_message', style={'fontWeight': 500}),])

        return trending_tt_summary_div, tt_data, tt_columns

    except:
        trending_tt_summary = 'Google API request limit reached. Try again after some time. ☹️'
        trending_tt_summary_div = html.Div([
            html.Div([], className='content_separator'),  # separator line
            html.H5([trending_tt_summary], className='content_message', style={'fontWeight': 500}),])

        return trending_tt_summary_div, tt_data, tt_columns
