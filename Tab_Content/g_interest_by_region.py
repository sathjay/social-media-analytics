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
from app import app

from pytrends.request import TrendReq
import country_converter as coco
import time


interest_by_Region_DF = pd.DataFrame()


def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None, plot_bgcolor='rgba(245, 245, 245, 0.93)',
                      paper_bgcolor='rgba(245, 245, 245, 0.93)')
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig


g_interest_by_region_lo = html.Div([
    html.H5(
        "Enter the item for which you want to find interest/popularity Country-wise:"),

    html.Div([
        dcc.Input(id="search_item_1",
                  type="text",
                  placeholder="Example: Beer or Chocolate",
                  required=True,
                  persistence=False,
                  style={'marginRight': '10px'},
                  className='input_box'),
    ], className='g_selection'),

    html.Br(),

    html.Button('Submit', id='submit-ibr', className='button', n_clicks=0),
    html.Br(),
    html.Div(id='g_ibr_message'),


    html.Br(),
    html.Div([
        dcc.Graph(id='ibr_plot', figure=blank_fig(),
                  style={'width': '90%', 'height': '60vh', 'margin-left': '10px', 'margin-right': '3%'}),

    ], className='graph_container'),

    html.Div([
        html.P("Popularity Country wise for the selected item:",
               className="response_title"),

        dash_table.DataTable(id='trending_ibr',
                             cell_selectable=False,
                             page_action="native",
                             page_current=0,
                             page_size=20,
                             style_header={
                                 'backgroundColor': 'rgb(62, 152, 211)',
                                 'fontSize': '18px',
                                 'fontWeight': 'bold',
                                 'textAlign': 'center',
                                 'color': 'white',
                                 'height': 'auto',
                                 'lineHeight': '15px', },
                             style_cell={
                                 'fontSize': '14px',
                                 'textAlign': 'center',
                             },
                             style_cell_conditional=[
                                 {
                                     'if': {'column_id': 'Rank'},
                                     'width': '16px',
                                     'textAlign': 'center'},
                                 {
                                     'if': {'column_id': 'Country'},
                                     'maxWidth': '130px',
                                     'textAlign': 'left',
                                     'textOverflow': 'ellipsis',
                                     'padding-left': '8px', },

                             ],

                             ),

    ], className='small_table'),


])


@app.callback(
    [Output('g_ibr_message', 'children'),
     Output('ibr_plot', component_property='figure'),
     Output('trending_ibr', component_property='data'),
     Output('trending_ibr', component_property='columns')],
    [Input('submit-ibr', 'n_clicks')],
    [State('search_item_1', 'value')],
    prevent_initial_call=True
)
def g_trend_ibr(n_click, search_item_1):

    KW_list = []

    print(type(search_item_1))
    if (search_item_1 == None):
        message = "Please enter input for topic or item of interest."
        return message

    search_item_1 = search_item_1.strip()
    KW_list = [search_item_1]
    message = ''

    if (len(search_item_1) == 0) or type(search_item_1) == None:
        message = "Please enter input"
    else:
        message = f'The Google Trends Relative Interest/Popularity for {search_item_1} accross the world:'

    message_output = html.Div([
        html.Div([], className='content_separator'),  # separator line

        html.H5([message], className='content_message')
    ])

    pytrends = TrendReq()

    pytrends.build_payload(kw_list=KW_list, cat=0,
                           timeframe='all', geo='', gprop='')

    df = pytrends.interest_by_region(resolution='COUNTRY',
                                     inc_low_vol=False,
                                     inc_geo_code=False).sort_values(KW_list[0], ascending=False)
    df = df.loc[(df != 0).any(axis=1)]
    # df = pd.to_numeric(df)
    df['Country'] = df.index
    df['country'] = coco.convert(
        names=df.Country.tolist(), to='ISO3', not_found=None)
    print(df)

    df1 = df[['Country', 'country', KW_list[0]]]
    df1["Rank"] = np.arange(1, len(df1) + 1)
    print(df1)

    df2 = df1[['Rank', 'Country', KW_list[0]]]

    fig = px.scatter_geo(df1, locations="country",
                         size=KW_list[0],
                         color=KW_list[0],
                         hover_name="Country",
                         projection="natural earth"

                         )

    r_columns = [{'name': col, 'id': col} for col in df2.columns]
    r_data = df2.to_dict(orient='records')

    return message_output, fig, r_data, r_columns
