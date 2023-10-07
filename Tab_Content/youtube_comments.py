from googleapiclient.discovery import build
import pandas as pd
import numpy as np
import re
import openai
import datetime

# Dash Interactive components
import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from app import app
from Tab_Content.zEnv_variables import stopwords, Youtube_API_Key, Open_AI_API_Key


from numerize import numerize # Added to make numbers readable.

api_key = Youtube_API_Key
youtube = build('youtube', 'v3', developerKey=api_key)
search_result_DF = pd.DataFrame()   
video_title = ''


openai.api_key = Open_AI_API_Key

def comment_clense(comment):
    '''Comments can have multiple spaces or tabs. This will cleanse it provide a single splace text.'''
    comment = ' '.join(comment.split())
    return comment

youtube_comments_lo = html.Div([

    html.P("Enter or paste the YouTube video link below and click Submit button. The app will:"),
    html.Div([
        html.Li("Extract the video title, total views, likes and comments that YouTube video has generated so far."),
        html.Li("Display a table with the top 20 comments on the video."),
        html.Li("If the user clicks on any comment, it will display the full comment, invoke ChatGPT to perform sentiment analysis on the comment, and generate a 'Thank you' message as a response for the commenter."),

    ], className='app_task_list'),
    html.Label("Enter YouTube Channel URL:", className='label'),

    dcc.Input(id="youtube_url_comment",
              type="url",
              value='https://www.youtube.com/watch?v=ILgSesWMUEI',
              # placeholder="Example: https://www.youtube.com/watch?v=FkKPsLxgpuY&t=640s ",
              required=True,
              persistence=False,
              style={'marginRight': '10px'},
              className='input_box'),
    html.Br(),
    html.Button('Submit', id='submit-youtube_url',
                className='button', n_clicks=0),
    html.Br(),
    html.P(id='video_search_message'),
    dash_table.DataTable(
        id='video_search_result',
        cell_selectable=True,
        page_action="native",
        page_current=0,
        page_size=10,
        style_header={
            'backgroundColor': 'rgb(62, 152, 211)',
            'fontSize': '18px',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'color': 'white',

        },
        style_cell={
            'fontSize': '14px'},

        style_cell_conditional=[
            {
                'if': {'column_id': 'Comment No:'},
                'width': '25px',
                'textAlign': 'center'
            },
            {
                'if': {'column_id': 'Author'},
                'maxWidth': '60px',
                'textAlign': 'left',
                'padding-left': '8px',
                'padding-left': '6px',
                'textOverflow': 'ellipsis',
            },
            {
                'if': {'column_id': 'Comment'},
                'maxWidth': '150px',
                'textAlign': 'left',
                'textOverflow': 'ellipsis',
                'padding-left': '8px',

            },
            {
                'if': {'column_id': 'Comment Like Count'},
                'width': '50px',
                'textAlign': 'center'
            }
        ]


    ),
    html.Div(id='comment_section'),
    html.Br(),
    html.Div(id="ChatGPT_response"),


])


@app.callback(
    [Output('video_search_message', 'children'),
     Output('video_search_result', component_property='data'),
     Output('video_search_result', component_property='columns'),
     Output("video_search_result", 'selected_cells'),
     Output("video_search_result", "active_cell"),
     Output("youtube_url_comment", component_property='value'),
     Output("comment_section", 'children', allow_duplicate=True),
     Output("ChatGPT_response", 'children', allow_duplicate=True)
     ],
    [Input('submit-youtube_url', 'n_clicks')],
    [State('youtube_url_comment', 'value')],
    prevent_initial_call=True
)
def chatgpt_layout1(n_click, search_term):
    '''Comments for a particular Youtube video is extracted and displayed in table form.
    The columns that will be displayed are comment number, comment author, comment(upto 140 char for display, 
    comment like count. 20 comments are fetched and 10 are displayed. Page navigation for table is configured. 

    This table is active. If user selects on a row, then comments in that row will be analyzed further by ChatGPT.
    '''
    
    link = search_term
    print(link)
    video_search_result_data = []
    video_search_result_column = []

    pattern = 'v='
    message = ''
    match = re.search(pattern, link)
    # Validating whether the link provided is valid or not.
    if match == None:
        message = "Please check the YouTube Video url. It should be like 'https://www.youtube.com/watch?v=RywP7cCYUWE' \
         or like 'https://www.youtube.com/watch?v=FkKPsLxgpuY&t=648s' this. "

        message_div = html.Div([
            html.Div([], className='content_separator'),
            html.H5([message], className='content_message')

        ])

    else:
        vid_start = match.end()
        vid_end = vid_start+11
        video_id = link[vid_start:vid_end]
        print(video_id)

        try:
            v_request = youtube.videos().list(
                part="snippet,statistics",
                id=video_id)
            v_response = v_request.execute()
            global video_title
            video_title = v_response['items'][0]['snippet']['title']

            video_view_count = int(
                v_response['items'][0]['statistics']['viewCount'])
            video_like_count = int(
                v_response['items'][0]['statistics']['likeCount'])
            video_comment_count = int(
                v_response['items'][0]['statistics']['commentCount'])
            print(video_title, '\n', video_view_count, '\n',
                  video_like_count, '\n', video_comment_count)

            message = f'The entered Youtube video url is "{link}". \nThe title of the video is "{video_title}". \nThis video has generated {numerize.numerize(video_view_count)} views with {numerize.numerize(video_like_count)} likes and {numerize.numerize(video_comment_count)} comments. \n\nBelow are the 20 top level comments: (Click on a row and scroll below to see the ChatGPTs response.)'

            message_div = html.Div([
                html.Div([], className='content_separator'),
                html.H6([message], className='content_message')

            ])
            
            c_request = youtube.commentThreads().list(
                part="id,snippet,replies",
                maxResults=20,
                order="relevance",
                videoId=video_id
            )

            c_response = c_request.execute()

            all_comments_info = []
            response_item = c_response['items']
            response_length = len(c_response['items'])

            for i in range(0, response_length):
                comments_row = {}
                comments_row['Comment No:'] = i+1
                comments_row['Author'] = response_item[i]['snippet']['topLevelComment']['snippet']['authorDisplayName']
                comments_row['Comment Like Count'] = response_item[i]['snippet']['topLevelComment']['snippet']['likeCount']
                comments_row['Comment'] = response_item[i]['snippet']['topLevelComment']['snippet']['textOriginal'][0:140]+"..."
                comments_row['Full Comment'] = response_item[i]['snippet']['topLevelComment']['snippet']['textOriginal']
                all_comments_info.append(comments_row)

            global all_comments_DF
            all_comments_DF = pd.DataFrame(all_comments_info)
            all_comments_DF['Full Comment'] = all_comments_DF['Full Comment'].apply(
                comment_clense)

            comment_Display_DF = all_comments_DF[[
                'Comment No:', 'Author', 'Comment', 'Comment Like Count']]
            comment_Display_DF = comment_Display_DF.reset_index().rename(columns={
                "index": "id"})

            print(all_comments_DF.head(5))

            video_search_result_column = [{'name': col, 'id': col}
                                          for col in comment_Display_DF.columns if col != 'id']
            video_search_result_data = comment_Display_DF.to_dict(
                orient='records')

        except:
            message = "Sorry. Either the comments are disabled for the video. Or issue your Youtube API"

        print(message)

    return message_div, video_search_result_data, video_search_result_column, [], None, '', None, None


@app.callback([Output('comment_section', "children"),
               Output('ChatGPT_response', "children"),],
              [Input('video_search_result', 'active_cell')],
              prevent_initial_call=True)
def chatgpt_layout2(active_cell):

    '''for the active cell, the comment is extracted and with some prompt engineering it is sent to ChatGPT to 
    analyze the sentiment and generate a thankyou response. The response for ChatGPT is displayed on the screen.'''
    
    if active_cell is None:
        raise PreventUpdate

    print(active_cell)
    row = active_cell['row_id']
    comment = all_comments_DF['Full Comment'][row]

    print(video_title)
    print(comment)

    comment_section = (html.P(['The full comment from viewer:'], className='response_title'),
                       html.P(comment, id='comment_section_p'))

    prompt = 'TITLE: ' + video_title + '\n' + 'COMMENT: '+comment
    print(prompt)

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': 'You are a Youtube content creator.\
                                     Guage the sentiment of the comment you recieved \
                                     for your video. List out the sentiment which could be positive, \
                                     negative or neutral and generate a thank you response. IF the sentiment is \
                                     negative then keep the thank you response short'},
            {'role': 'user', 'content': prompt}

        ]

    )

    # Converting the ChatGPT response from string to List

    chat_gpt_response = response['choices'][0]['message']['content'].split(
        '\n')

    chat_gpt_response = list(filter(None, chat_gpt_response))
    sentiment = chat_gpt_response[0]
    ty_message = chat_gpt_response[1]

    chat_gpt_response_section = (html.P(["ChatGPT's Sentiment Analysis and Thankyou Message: "], className='response_title'),
                                 html.P(sentiment, id='sentiment'),
                                 html.P('ChatGPT Generated Thank you message:'),
                                 html.P(ty_message)
                                 )

    return comment_section, chat_gpt_response_section
