from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
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

# Added to make numbers readable.
from numerize import numerize


api_key = Youtube_API_Key
youtube = build('youtube', 'v3', developerKey=api_key)

search_result_DF = pd.DataFrame()
video_title = ''


openai.api_key = Open_AI_API_Key

youtube_transcript_lo = html.Div([

    html.P("Enter or paste the YouTube video link below and click Submit button. The app will:"),
    html.Div([
        html.Li("Extract the video title, total views, likes, comments that YouTube video has generated so far and the video transcript."),
        html.Li("Using ChatGPT, the app will provide PG/Adult rating, identify the key topics discussed in the video, and generate a summary of the video transcript."),
        html.Li("The app will also calculate the subjectivity and polarity of the conversation in the transcript of video by using TextBlob library."),

    ], className='app_task_list'),

    html.Label("Enter YouTube Channel URL:", className='label'),

    dcc.Input(id="youtube_url_transcript",
              type="url",
              placeholder="Example: https://www.youtube.com/watch?v=FkKPsLxgpuY&t=640s ",
              required=True,
              style={'marginRight': '10px'},
              persistence=False,
              className='input_box'),
    html.Br(),
    html.Button('Submit', id='submit-youtube_url',
                className='button', n_clicks=0),

    html.Br(),
    html.Div(id='video_tran_search_message'),

    html.Br(),
    html.Div(id='output-div'),
    html.Br(),

    html.Div(id='textarea-div'),

])


@app.callback(
    [Output('video_tran_search_message', 'children'),
     Output('output-div', 'children'),
     Output('textarea-div', 'children'),
     Output("youtube_url_transcript", component_property='value')],
    [Input('submit-youtube_url', 'n_clicks')],
    [State('youtube_url_transcript', 'value')],
    prevent_initial_call=True
)
def chatgpt_yt_content_analysis(n_clicks, video_url):

    pattern = 'v='
    message = ''
    match = re.search(pattern, video_url)
    if match == None:
        message = f"The Entered URL: {video_url}.\nPlease check the YouTube Video url. It should be like 'https://www.youtube.com/watch?v=RywP7cCYUWE' \
         or like 'https://www.youtube.com/watch?v=FkKPsLxgpuY&t=648s' this."

        message_div = html.Div([
            html.Div([], className='content_separator'),
            html.H5([message], className='content_message')

        ])

        return message_div, '', '', ''
    video_id = video_url.split('v=')[-1][0:11]

    v_request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id)
    v_response = v_request.execute()
    video_title = v_response['items'][0]['snippet']['title']

    video_view_count = int(
        v_response['items'][0]['statistics']['viewCount'])
    video_like_count = int(
        v_response['items'][0]['statistics']['likeCount'])
    video_comment_count = int(
        v_response['items'][0]['statistics']['commentCount'])
    print(video_title, '\n', video_view_count, '\n',
          video_like_count, '\n', video_comment_count)

    message = f'The entered Youtube video url is "{video_url}". \nThe title of the video is "{video_title}". \nThis video has generated {numerize.numerize(video_view_count)} views with {numerize.numerize(video_like_count)} likes and {numerize.numerize(video_comment_count)} comments.'

    message_div = html.Div([
        html.Div([], className='content_separator'),
        html.H6([message], className='content_message')

    ])

    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    print(transcript[0]['text'])

    full_transcrpit_list = []
    for i in range(0, len(transcript)-1):
        full_transcrpit_list.append(transcript[i]['text'])

    full_transcrpit = ' '.join(full_transcrpit_list)

    print(full_transcrpit)

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': 'You are a Youtube content moderator. Review the transcript of the video. You should list out the following:\
                                    1) The first item should be the rating on whether the content is appropriate for all audience or adults only or for kids. \
                                    2) The second item should be the keywords (Max 10 numbers based on importance) that are discussed in the video. \
                                    3) The third item should be the summary of the video transcpit no more than 200 words. '},

            {'role': 'user', 'content': full_transcrpit[0:5000]}


        ])

    print(response['choices'][0])

    response_text = response['choices'][0]['message']['content']

    text_area_content = html.Div([
        html.Label("The Full Transcript:", className='label'),
        html.Br(),
        dcc.Textarea(
            value=full_transcrpit,
            id='textarea-transcript',
            style={'width': '50%', 'height': 200},
        ),
    ])

    return message_div, response_text, text_area_content, ''
