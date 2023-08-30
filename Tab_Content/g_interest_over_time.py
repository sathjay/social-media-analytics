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


country_code_df = pd.read_csv(
    './assets//ISO_Country_Codes.csv', index_col='name')

country_drop_down_list = []
for i in range(0, len(country_code_df)):
    country_drop_down_list.append({'label': country_code_df.index[i],
                                   'value': country_code_df['alpha-2'][i]})
# Inserting Global as its is not present in courtry code list
country_drop_down_list.insert(0, {'label': 'Global', 'value': ''})

time_frame_dropdown_list = [
    {'label': '3 month', 'value': 'today 3-m'},
    {'label': '6 month', 'value': 'today 6-m'},
    {'label': '1 Year', 'value': 'today 12-m'},
    {'label': '5 Year', 'value': 'today 5-y'},
    {'label': 'For All', 'value': 'all'}]


def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None, plot_bgcolor='rgba(245, 245, 245, 0.93)',
                      paper_bgcolor='rgba(245, 245, 245, 0.93)')
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig


g_interest_over_time_lo = html.Div([
    html.H5("Enter up to 3 search topics (separated by commas) for which user want to find interest over time, country-wise:"),


    html.Div([

        dcc.Input(id="search_item_iot",
                  type="text",
                  placeholder="Example: Beer, Whisky, Wine",
                  required=True,
                  persistence=False,
                  style={'marginRight': '10px'},
                  className='input_box'),


        dcc.Dropdown(id='country_code_bt',
                     options=country_drop_down_list,
                     optionHeight=35,
                     disabled=False,  # disable dropdown value selection
                     multi=False,  # allow multiple dropdown values to be selected
                     searchable=True,  # allow user-searching of dropdown values
                     # gray, default text shown when no option is selected
                     placeholder='Select Country',
                     clearable=True,  # allow user to removes the selected value
                     className='dropdown_box',  # activate separate CSS document in assets folder
                     ),


        dcc.Dropdown(id='timeframe',
                     options=time_frame_dropdown_list,
                     optionHeight=35,
                     disabled=False,  # disable dropdown value selection
                     multi=False,  # allow multiple dropdown values to be selected
                     searchable=True,  # allow user-searching of dropdown values
                     # gray, default text shown when no option is selected
                     placeholder='Select Timeframe',
                     clearable=True,  # allow user to removes the selected value
                     className='dropdown_box',  # activate separate CSS document in assets folder
                     ),
    ], className='g_selection'),

    html.Br(),
    html.Button('Submit', id='submit-iot', className='button', n_clicks=0),
    html.Div(id='g_iot_message'),


    html.Div([
        dcc.Graph(id='interest_over_time_plot', figure=blank_fig(),
                  style={'width': '90%', 'height': '60vh', 'margin-left': '10px', 'margin-right': '3%'}),
    ], className='graph_container'),


])


@app.callback(
    [Output('g_iot_message', 'children'),
     Output('interest_over_time_plot', 'figure'),],
    [Input('submit-iot', 'n_clicks')],
    [State('search_item_iot', 'value'),
     State('country_code_bt', 'value'),
     State('timeframe', 'value')],
    prevent_initial_call=True
)
def g_trend_iot_layout(n_click, search_item_iot, country_code_bt, timeframe):

    if country_code_bt == None or timeframe == None:
        message = 'Please select the country and timeframe'
        message_div = html.Div([
            html.Div([], className='content_separator'),  # separator line
            html.H5([message], className='content_message')
        ])

        return message_div, blank_fig()

    search_item = search_item_iot
    KW_list = search_item.split(',')
    print(KW_list)
    print(type(KW_list))

    country_name = country_code_df.loc[country_code_df['alpha-2']
                                       == country_code_bt].index.values[0]

    if len(KW_list) > 3:
        return 'Please enter upto 3 search items', blank_fig()

    message = f"The Google Trends Interest over time at {country_name} for entered items:"
    message_list = ''

    for i in range(0, len(KW_list)):
        message_list = message_list + ' ' + str(i+1) + ") " + KW_list[i]

    full_message = message + message_list + ' :'

    message_div = html.Div([
        html.Div([], className='content_separator'),
        html.H5([full_message], className='content_message')
    ])

    pytrends = TrendReq()
    pytrends.build_payload(kw_list=KW_list, cat=0,
                           timeframe=timeframe, geo=country_code_bt, gprop='')
    df = pytrends.interest_over_time()
    df.drop('isPartial', axis=1, inplace=True)

    print(df)

    interest_over_time_plot_data = []

    for item in KW_list:
        trace = go.Scatter(x=df.index.values,
                           y=df[item],
                           mode='lines',
                           name=item)
        interest_over_time_plot_data.append(trace)

    plot_layout = go.Layout(
        title=dict(
            text=f'Google Trends Interest over time at {country_name}', x=.05, y=.95),
        yaxis=dict(title='Relative Interest',
                   showline=True,
                   linecolor='black',
                   showgrid=True,),
        xaxis=dict(title='Date',
                   showline=True,
                   linecolor='black',
                   showgrid=True,),
        showlegend=True,
        plot_bgcolor='white',
        legend=dict(
            bgcolor='white',
            bordercolor='black',
            orientation='h',
            x=.75,
            y=1.10,
            traceorder='normal',
            borderwidth=1)
    )

    Interest_over_time_fig = go.Figure(
        data=interest_over_time_plot_data, layout=plot_layout)

    return message_div, Interest_over_time_fig
