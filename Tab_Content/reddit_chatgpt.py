import praw

import pandas as pd
import numpy as np
import openai


# Plotly Graphing Libraries
import plotly
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from app import app

from Tab_Content.zEnv_variables import Reddit_id, Reddit_secret, Open_AI_API_Key


def comment_clense(comment):
    comment = ' '.join(str(comment).split())
    return comment


post_info_DF = pd.DataFrame()

user_agent = "Scraper by /u/sathgo"
reddit = praw.Reddit(client_id=Reddit_id,
                     client_secret=Reddit_secret, user_agent=user_agent,)

openai.api_key = Open_AI_API_Key

reddit_dropdown_feature = [
    {'label': 'r/investing', 'value': 'investing'},
    {'label': 'r/stocks', 'value': 'stocks'}
]


reddit_chatgpt_lo = html.Div([

    html.P("Select a finance subreddit handle from the dropdown and click the Submit button. The app will:"),
    html.Div([
        html.Li("Display the number of active users in the selected subreddit."),
        html.Li("Extract the top posts from the selected subreddit and display a table showing each post's Reddit rank, title, author, article snippets, and post ID."),
        html.Li("If the user clicks on any row, ChatGPT will be invoked to identify the Company/Stock discussed in the article, summarize the article, and perform sentiment analysis on the article and the first five comments it has received."),
        html.Li(
            "Subsequently, the app will display the full post title, article, and top five comments."),



    ], className='app_task_list'),



    html.Label(['Select the subreddit from the dorp down:'],
               className='label'),
    html.Br(),

    dcc.Dropdown(id='reddit_dropdown',
                 options=reddit_dropdown_feature,
                 optionHeight=35,
                 disabled=False,  # disable dropdown value selection
                 multi=False,  # allow multiple dropdown values to be selected
                 searchable=True,  # allow user-searching of dropdown values
                 # gray, default text shown when no option is selected
                 placeholder='Please select...',
                 clearable=True,  # allow user to removes the selected value
                 className='dropdown_box',  # activate separate CSS document in assets folder
                 ),
    html.Br(),

    html.Button('Start', id='reddit_chatgpt_submit',
                className='button', n_clicks=0),

    dcc.Loading(children=[

        html.Div(id='reddit_chatgpt_message'),
        # 'Rank', 'Title', 'Author', 'Article', 'Post_ID'
        dash_table.DataTable(id='reddit_article_table',
                             cell_selectable=True,
                             page_action="native",
                             page_current=0,
                             page_size=15,
                             style_header={
                                 'backgroundColor': 'rgb(62, 152, 211)',
                                 'fontSize': '18px',
                                 'fontWeight': 'bold',
                                 'textAlign': 'center',
                                 'color': 'white'},
                             style_cell={
                                 'fontSize': '14px'},
                             style_cell_conditional=[
                                 {
                                     'if': {'column_id': 'Rank'},
                                     'width': '15px',
                                     'textAlign': 'center'},
                                 {
                                     'if': {'column_id': 'Title'},
                                     'maxWidth': '120px',
                                     'textAlign': 'left',
                                     'padding-left': '8px',
                                     'padding-left': '6px',
                                     'textOverflow': 'ellipsis', },
                                 {'if': {'column_id': 'Author'},
                                  'maxWidth': '60px',
                                  'textAlign': 'left',
                                  'padding-left': '8px',
                                  'padding-left': '6px',
                                  'textOverflow': 'ellipsis', },
                                 {
                                     'if': {'column_id': 'Article'},
                                     'maxWidth': '240px',
                                     'textAlign': 'left',
                                     'padding-left': '8px',
                                     'padding-left': '6px',
                                     'textOverflow': 'ellipsis', },
                                 {
                                     'if': {'column_id': 'Post_ID'},
                                     'maxWidth': '60px',
                                     'textAlign': 'center',
                                     'padding-left': '8px',
                                     'padding-left': '6px',
                                     'textOverflow': 'ellipsis', }
                             ]
                             ),

    ], type="circle", fullscreen=True),

    dcc.Loading(children=[
        html.Div(id="Reddit_ChatGPT_response"),
        html.Br(),
        html.Div(id='Reddit_comment_section'),

    ], type="circle", fullscreen=True),


])


@app.callback(
    [Output('reddit_chatgpt_message', 'children'),
     Output('reddit_article_table', component_property='data'),
     Output('reddit_article_table', component_property='columns'),
     Output("reddit_article_table", 'selected_cells'),
     Output("reddit_article_table", "active_cell"),
     Output("Reddit_ChatGPT_response",  'children', allow_duplicate=True),
     Output("Reddit_comment_section",  'children', allow_duplicate=True),
     ],
    [Input('reddit_chatgpt_submit', 'n_clicks')],
    [State('reddit_dropdown', 'value')],
    prevent_initial_call=True
)
def reddit_chatgpt_layout(n_click, sub_reddit):
    print(n_click)

    subreddit = reddit.subreddit(sub_reddit)
    rname = subreddit.display_name
    title = subreddit.title
    active_account = subreddit.accounts_active

    message1 = f"SubReddit handle r/{rname} - '{title}' has {active_account} active accounts."

    message2 = "Following are the Hot posts within selected subreddit handle: (Click on any row below to invoke ChatGPT and scroll down to see the response)"

    posts = subreddit.hot(limit=62)

    post_info = []
    rank = -1
    for post in posts:
        post = dict(
            Rank=rank,
            Title=post.title[0:40]+"...",
            Full_Title=post.title,
            Author=post.author,
            Article=post.selftext[0:90]+"...",
            Full_Article=post.selftext,
            Post_ID=post.id)
        post_info.append(post)
        rank = rank+1

    # First two article are pinned posts from Reddit. Hence excluding them.
    post_info = post_info[2:len(post_info)]

    global post_info_DF
    post_info_DF = pd.DataFrame.from_dict(post_info)

    post_info_DF['Title'] = post_info_DF['Title'].apply(comment_clense)
    post_info_DF['Full_Title'] = post_info_DF['Full_Title'].apply(
        comment_clense)
    post_info_DF['Author'] = post_info_DF['Author'].apply(comment_clense)
    post_info_DF['Article'] = post_info_DF['Article'].apply(comment_clense)
    post_info_DF['Full_Article'] = post_info_DF['Full_Article'].apply(
        comment_clense)

    reddit_display_DF = post_info_DF[[
        'Rank', 'Title', 'Author', 'Article', 'Post_ID']]
    reddit_display_DF = reddit_display_DF.reset_index().rename(columns={
        "index": "id"})

    print(reddit_display_DF.head(5))
    print(type(reddit_display_DF))

    reddit_message = html.Div([
        html.Div([], className='content_separator'),  # separator line
        html.Br(),
        html.H5(message1),
        html.H5(message2),


    ])

    print(message1)
    print(message2)

    reddit_article_table_data = reddit_display_DF.to_dict(orient='records')
    reddit_article_table_columns = [{'name': col, 'id': col}
                                    for col in reddit_display_DF.columns if col != 'id']

    return reddit_message, reddit_article_table_data, reddit_article_table_columns, [], None, None, None


@app.callback([Output('Reddit_ChatGPT_response', "children"),
               Output('Reddit_comment_section', "children")],
              [Input('reddit_article_table', 'active_cell')],
              prevent_initial_call=True
              )
def chatgpt_layout2(active_cell):
    if active_cell is None:
        raise PreventUpdate

    print(active_cell)

    row_id = active_cell['row_id']

    submission_id = post_info_DF['Post_ID'][row_id]

    submission = reddit.submission(submission_id)

    # print(submission.title)
    title = "TITLE: " + submission.title + '\n\n'

    # print(submission.selftext)
    article_text = "ARTICLE: " + submission.selftext + '\n\n'

    all_comments = submission.comments
    comments = ''
    if len(all_comments) >= 7:
        comment_limit = 7
    else:
        comment_limit = len(all_comments)

    comment_count = 1
    comment_list = []
    for comment in all_comments:
        if comment_count == 1:  # Skipping the first comment as it is having user report.
            comment_count = comment_count+1
            pass

        if (comment_count > 1) and (comment_count < comment_limit):
            comment_body = comment.body
            # The display will start from 1 else if will start from 2 because the fist is ignored.
            comment_ct = comment_count-1
            comment_list.append(str(comment_ct) + ':-> ' + comment_body)
            comments = comments + str(comment_ct) + \
                ':-> ' + comment_body + '\n'

            comment_count = comment_count+1
        if comment_count == comment_limit:
            break

    comments = "COMMENTS: \n\n" + comments
    print(len(all_comments))
    print(comments)

    prompt = title+article_text+comments

    print(prompt)

    Reddit_comment_section = html.Div([
        html.H5(["Full article from Reddit with top 5 comments:"],
                style={'fontWeight': 500}),
        html.P([prompt],
               style={'whiteSpace': 'pre-wrap'}
               ),

    ])

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': "You are a stock research analyst.You are analyzing a reddit post. Analyze the TITLE, ARTICLE and COMMENTS. The response should be in specified format with 3 bullet points. First bullet point should be'Ticker/Companies/Sector/ETF:' which should list all the stock tickers or companies or ETF or sector being discussed in the article section in one sentence. If no ticker or company is mentioned then write No company mentioned. Second bullet point should be called 'Article Summary and Sentiment:' and in one paragraph it should give a brief summary of ARTICLE section and Classify the sentiment of Article- bullish or bearish or neutral. Third bullet point should be called 'Comments Summary and Sentiments:', and should give summary and sentiments of comments in one paragraph."},
            {'role': 'user', 'content': prompt}

        ],
        presence_penalty=.2


    )

    print('***Response****')
    print(response["choices"][0]['message']['content'])
    chatGPT_response = response["choices"][0]['message']['content']

    Reddit_ChatGPT_response = html.Div([
        html.H5(["ChatGPT's Analysis of the Article:"],
                style={'fontWeight': 500}),
        html.P([chatGPT_response],
               style={'whiteSpace': 'pre-wrap'})

    ])

    return Reddit_ChatGPT_response, Reddit_comment_section
