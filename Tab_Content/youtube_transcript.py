from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi  # Free API used to extract transcript from the video.
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
        html.Li(
            "The app will also provide the sentiment of the conversation in the video transcript.")

    ], className='app_task_list'),

    html.Label("Enter YouTube Channel URL:", className='label'),

    dcc.Input(id="youtube_url_transcript",
              type="url",
              value='https://www.youtube.com/watch?v=ILgSesWMUEI',
              # placeholder="Example: https://www.youtube.com/watch?v=FkKPsLxgpuY&t=640s ",
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
    html.Div(id='response-div'),
    html.Br(),

    html.Div(id='textarea-div'),

])


@app.callback(
    [Output('video_tran_search_message', 'children'),
     Output('response-div', 'children'),
     Output('textarea-div', 'children'),
     Output("youtube_url_transcript", component_property='value')],
    [Input('submit-youtube_url', 'n_clicks')],
    [State('youtube_url_transcript', 'value')],
    prevent_initial_call=True
)
def chatgpt_yt_content_analysis(n_clicks, video_url):
    ''' From the user provided Youtube url, video id is extracted.
    Using that video ID, full transcript is extracted, parsed and send to ChatGPT to check for PG/Adult rating, list of key words
    Summary of Transcript and Sentiment.'''

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

    if len(full_transcrpit) > 5000:
        transcript_length = 5000
    else:
        transcript_length = len(full_transcrpit)

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': 'You are a Youtube content moderator. Review the transcript of the video. You should list out the following:\
                                    1) The first item should be the rating on whether the content is appropriate for all audience or adults only or for kids. \
                                    2) The second item should be top 10 keywords that are discussed in the video. \
                                    3) The third item should be the summary of the video transcpit no more than 200 words.\
                                    4) The fourth item should be the sentiment of the conversation in the video transcript.\
            The output should have 4 points and listed as 1),2),3) and 4) '
             },

            {'role': 'user', 'content': full_transcrpit[0:transcript_length]}

        ])

    chat_gpt_transcript_analysis = response['choices'][0]['message']['content'].split(
        '\n')
    print(chat_gpt_transcript_analysis)
    chat_gpt_transcript_analysis_updated = []

    for item in chat_gpt_transcript_analysis:
        if len(item) > 1:
            chat_gpt_transcript_analysis_updated.append(item)
        else:
            pass

    print(chat_gpt_transcript_analysis_updated)

    rating = chat_gpt_transcript_analysis_updated[0]
    keywords = chat_gpt_transcript_analysis_updated[1]
    summary = chat_gpt_transcript_analysis_updated[2]
    sentiment = chat_gpt_transcript_analysis_updated[3]

    response_div = (html.P(["ChatGPT's Transcript Analysis  "], className='response_title'),
                    html.P(rating, id='rating'),
                    html.P(keywords, id='keywords'),
                    html.P(summary, id='summary'),
                    html.P(sentiment, id='sentiment'),
                    html.P(
                        'Note: Only first 5000 characters of the transcript is used for analysis. This is beacuse of the API token limit from  OpenAI.', className='note')
                    )

    text_area_content = html.Div([
        html.Label("The Full Transcript:", className='label'),
        html.Br(),
        dcc.Textarea(
            value=full_transcrpit,
            id='textarea-transcript'
        ),
    ])

    return message_div, response_div, text_area_content, ''
