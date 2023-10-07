import praw
import pandas as pd
import numpy as np
import re
import emoji
from textblob import TextBlob
from datetime import datetime
from wordcloud import WordCloud

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

from Tab_Content.zEnv_variables import stopwords, Reddit_id, Reddit_secret, popular_subreddit


popular_items_dropdown_list = []
for i in range(0, len(popular_subreddit)):
    popular_items_dropdown_list.append({'label': popular_subreddit[i],
                                        'value': popular_subreddit[i]})


def calSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity


def calPolarity(text):
    return TextBlob(text).sentiment.polarity


def clean_text(txt):
    '''
    This is used to remove all the special characters/spaces/tabs and emoji's.
    
    '''
    txt = re.sub(r"RT[\s]+", "", txt)
    txt = txt.replace("\n", " ")
    txt = re.sub(" +", " ", txt)
    txt = re.sub(r"https?:\/\/\S+", "", txt)
    txt = re.sub(r"(@[A-Za-z0–9_]+)|[^\w\s]|#", "", txt)
    txt = emoji.replace_emoji(txt, replace='')
    txt.strip()
    return txt


def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None, plot_bgcolor='rgba(245, 245, 245, 0.93)',
                      paper_bgcolor='rgba(245, 245, 245, 0.93)')
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)


user_agent = "Scraper by /u/sathgo"
reddit = praw.Reddit(client_id=Reddit_id,
                     client_secret=Reddit_secret,
                     user_agent=user_agent,)

reddit_text_blob_lo = html.Div([

    html.P("Select a popular subreddit handle from the dropdown and click the Submit button. The app will:"),
    html.Div([
        html.Li("Extract the top 100 posts from the subreddit and display a table showing each post's Reddit rank, title, created date, author, Reddit score, upvote ratio, subjectivity and polarity of the title, and post URL."),
        html.Li(
            "The subjectivity and polarity of each title are calculated using TextBlob and the app will also display the mean subjectivity and polarity of all the titles from this subreddit. "),
        html.Li(
            "The app will also display a WordCloud of the top 100 titles from the subreddit handle."),

    ], className='app_task_list'),

    dcc.Dropdown(id='subreddit_drop_down',
                 options=popular_items_dropdown_list,
                 optionHeight=35,
                 disabled=False,  # disable dropdown value selection
                 multi=False,  # allow multiple dropdown values to be selected
                 searchable=True,  # allow user-searching of dropdown values
                 value='Politics',  # default value
                 # placeholder='Select SubReddit like ChatGPT or Politics',
                 clearable=True,  # allow user to removes the selected value
                 className='dropdown_box',  # activate separate CSS document in assets folder
                 ),

    html.Br(),
    html.Button('Submit', id='reddit_submit', className='button', n_clicks=0),


    dcc.Loading(children=[
        html.Br(),
        html.Div(id='reddit_message_div'),

        html.Br(),

        html.Div([
            html.Div(id='reddit_table'),
        ], className='large_table'),

        html.Br(),

        html.Div(id='reddit_wordcloud_figure_div', children=""),

    ], type="circle", fullscreen=True),

])


@app.callback(
    [Output('reddit_message_div', 'children'),
     Output('reddit_table', 'children'),
     Output("reddit_wordcloud_figure_div", "children"),
     ],
    [Input('reddit_submit', 'n_clicks')],
    [State('subreddit_drop_down', 'value')],
    prevent_initial_call=True
)
def reditt_analysis(n_clicks, value):

    search_term = value

    thread = reddit.subreddit(search_term).hot(limit=100)

    reddit_message = f"Below are the 100 Hot threads returned from Reddit for 'r/{search_term}' subreddit:"

    heading_row = []
    for article in thread:
        heading_row.append([article.title,
                            datetime.utcfromtimestamp(
                                article.created_utc).strftime('%Y-%m-%d'),
                            article.author.name,
                            article.score,
                            article.upvote_ratio,
                            article.shortlink,
                            ])

    columns = ['Title', 'Created', 'Author',
               'Score', 'UpVote Ratio', 'SubReddit URL']

    thread_heading = pd.DataFrame(heading_row, columns=columns)

    thread_heading['Cleaned_title'] = thread_heading['Title'].apply(clean_text)

    thread_heading['Subjectivity'] = thread_heading['Cleaned_title'].apply(
        calSubjectivity).round(2)
    thread_heading['Polarity'] = thread_heading['Cleaned_title'].apply(
        calPolarity).round(2)

    thread_heading["Rank"] = np.arange(1, len(thread_heading) + 1)

    thread_heading_Display_DF = thread_heading[['Rank', 'Title', 'Created', 'Author',
                                                'Score', 'UpVote Ratio', 'Subjectivity',
                                                'Polarity']]

    # r_columns = [{'name':col, 'id':col} for col in thread_heading_Display_DF.columns]
    # r_data = thread_heading_Display_DF.to_dict(orient = 'records')

    mean_subjectivity = thread_heading[['Subjectivity']].mean().round(3)
    mean_polarity = thread_heading[['Polarity']].mean().round(3)

    reddit_summary = f'\nThe subreddit {search_term} titles have a mean Subjectivity of {mean_subjectivity[0]} and mean Polarity of {mean_polarity[0]}.\nThe subjectivity and polarity of the title are calculated using TextBlob.'

    reddit_message_div = html.Div([
        html.Div([], className='content_separator'),
        html.H6([reddit_message + reddit_summary],
                className='content_message'),
        # html.H6([reddit_summary], className='content_message'),
    ])

    print('Mean Subjectivity =', mean_subjectivity)
    print('Mean Polarity =', mean_polarity)

    thread_heading['title_no_stopwords'] = thread_heading['Cleaned_title'].apply(
        lambda x: [item for item in str(x).split() if item not in stopwords])

    reddit_table = dash_table.DataTable(
        id='reddit_result',
        cell_selectable=False,
        data=thread_heading_Display_DF.to_dict(orient='records'),
        columns=[{'name': col, 'id': col}
                 for col in thread_heading_Display_DF.columns],
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
                    'lineHeight': '15px'
        },
        style_cell={
            'fontSize': '14px'},
        style_cell_conditional=[
            {
                'if': {'column_id': 'Rank'},
                'width': '16px',
                'textAlign': 'center'},
            {
                'if': {'column_id': 'Title'},
                'maxWidth': '440px',
                'textAlign': 'left',
                'textOverflow': 'ellipsis',
                'padding-left': '8px', },
            {
                'if': {'column_id': 'Created'},
                'width': '22px',
                'textAlign': 'center'},
            {
                'if': {'column_id': 'Author'},
                'width': '60px',
                'textAlign': 'left',
                'padding-left': '6px', },
            {
                'if': {'column_id': 'Score'},
                'width': '16px',
                'textAlign': 'center'},
            {
                'if': {'column_id': 'UpVote Ratio'},
                'width': '16px',
                'textAlign': 'center'},
            {
                'if': {'column_id': 'Subjectivity'},
                'width': '16px',
                'textAlign': 'center'},
            {
                'if': {'column_id': 'Polarity'},
                'width': '16px',
                'textAlign': 'center'},
        ]

    )

    title_with_no_stopword_list = list(
        [a for b in thread_heading['title_no_stopwords'].tolist() for a in b])

    title_with_no_stopword_list_str = ' '.join(title_with_no_stopword_list)

    print(title_with_no_stopword_list_str)

    my_wordcloud = WordCloud(width=2450, height=1500, random_state=1, background_color='black',
                             colormap='viridis', collocations=False).generate(title_with_no_stopword_list_str)

    # visualize wordcloud inside plotly figure
    fig = px.imshow(my_wordcloud, template='ggplot2')
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    wordcloud_Fig = dcc.Graph(figure=fig, config={"displayModeBar": False}, style={
        'width': '90%', 'height': '74vh'})

    wordcloud_Fig_title = f'WordCloud for the titles in subreddit {search_term}:'

    reddit_wordcloud_figure_div = html.Div([html.P(wordcloud_Fig_title, className='response_title'),
                                            wordcloud_Fig
                                            ], className='graph_container')

    return reddit_message_div, reddit_table,  reddit_wordcloud_figure_div
