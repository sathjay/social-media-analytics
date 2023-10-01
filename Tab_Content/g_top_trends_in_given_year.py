import pandas as pd
import numpy as np
import datetime
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
    './assets//ISO_Country_Codes.csv', index_col='name')

country_drop_down_list = []
for i in range(0, len(country_code_df)):
    country_drop_down_list.append({'label': country_code_df.index[i],
                                   'value': country_code_df['alpha-2'][i]})
# Inserting Global as its is not present in courtry code list
country_drop_down_list.insert(0, {'label': 'Global', 'value': 'GLOBAL'})


year_drop_down_list = []
today = datetime.date.today()
year = today.year

for i in range(2018, year, 1):
    year_drop_down_list.append({'label': i, 'value': i})

g_top_trends_in_given_year_lo = html.Div([
    html.H5("Google Trends: Top Trends in a given year"),
    html.Div([
        html.Label(["Select a Country and year from the dorp down to see what's trending there in given year:"],
                   className='label'),

        dcc.Dropdown(id='country_code_bt',
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



        dcc.Dropdown(id='year_drop_down_bt',
                     options=year_drop_down_list,
                     optionHeight=35,
                     disabled=False,  # disable dropdown value selection
                     multi=False,  # allow multiple dropdown values to be selected
                     searchable=True,  # allow user-searching of dropdown values
                     value='2022',
                     # placeholder='Select Year',  # gray, default text shown when no option is selected
                     clearable=True,  # allow user to removes the selected value
                     className='dropdown_box',  # activate separate CSS document in assets folder
                     ),
    ], className='g_selection'),

    html.Br(),


    html.Button('Submit', id='submit_ctry_bt', className='button', n_clicks=0),
    html.Div(id='trending_y_summary_div'),
    html.Div([
        dash_table.DataTable(id='trending_bt',
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
                                 'fontSize': '14px',
                                 'textAlign': 'center',
                             },
                             style_cell_conditional=[
                                 {
                                     'if': {'column_id': 'Rank'},
                                     'width': '18px',
                                     'textAlign': 'center'},
                             ],

                             )
    ], className='small_table'),
    html.Br(),
])


@app.callback(
    [Output('trending_y_summary_div', 'children'),
     Output('trending_bt', component_property='data'),
     Output('trending_bt', component_property='columns'),
     ],
    [Input('submit_ctry_bt', 'n_clicks')],
    [State('country_code_bt', 'value'),
     State('year_drop_down_bt', 'value')],
    prevent_initial_call=True
)
def update_been_trending(n_clicks, country_code_bt, year_drop_down_bt):

    ctry_cd = [country_code_bt]
    print(ctry_cd)
    print(type(ctry_cd))
    pytrend = TrendReq()
    top_chart_result = []
    year_selected = year_drop_down_bt
    print(year_selected)

    if ctry_cd == None or year_selected == None:
        trending_bt_summary = "Please select a Country and Year from the drop down!"
        bt_data = []
        bt_columns = []
        trending_y_summary_div = html.Div([
            html.Div([], className='content_separator'),  # separator line
            html.H5([trending_bt_summary], className='content_message', style={'fontWeight': 500}),])
        return trending_y_summary_div, bt_data, bt_columns

    else:
        for country in ctry_cd:
            ctry_df = pd.DataFrame()
            ctry_df = pytrend.top_charts(
                year_selected, hl='en-US', geo=country)[['title']]

            country_name = country_code_df.loc[country_code_df['alpha-2']
                                               == country].index.values[0]

            if country == 'GLOBAL':
                ctry_df.rename(columns={'title': 'Global'}, inplace=True)
            else:
                ctry_df.rename(columns={
                               'title': country_name}, inplace=True)

            top_chart_result.append(ctry_df)

        # each country code result is a dataframe in the top_chart_result hence combining the dataframe.

        top_chart_result_DF = pd.concat(top_chart_result, axis=1)
        top_chart_result_DF["Rank"] = np.arange(
            1, len(top_chart_result_DF) + 1)
        rank_column = top_chart_result_DF.pop('Rank')
        top_chart_result_DF.insert(0, 'Rank', rank_column)

    bt_columns = [{'name': col, 'id': col}
                  for col in top_chart_result_DF.columns]
    bt_data = top_chart_result_DF.to_dict(orient='records')

    country_name = country_code_df.loc[country_code_df['alpha-2']
                                       == country].index.values[0]

    trending_bt_summary = f"The top 10 terending searches for year {year_selected} in {country_name} are:"
    trending_y_summary_div = html.Div([
        html.Div([], className='content_separator'),  # separator line
        html.H5([trending_bt_summary], className='content_message', style={'fontWeight': 500}),])

    return trending_y_summary_div, bt_data, bt_columns
