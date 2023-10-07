# Get all packages
from googleapiclient.discovery import build
import pandas as pd
import numpy as np
import re
# Plotly Graphing Libraries
import plotly
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
# Dash Packages and Library 
import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from app import app

from numerize import numerize # Added to make numbers readable.
from dateutil import parser # Added to reformat the timestamps
from Tab_Content.zEnv_variables import stopwords
from Tab_Content.zEnv_variables import Youtube_API_Key
from wordcloud import WordCloud

# API setup and configuration
api_key = Youtube_API_Key
youtube = build('youtube', 'v3', developerKey=api_key)
stopwords = stopwords
search_result_DF = pd.DataFrame()
all_comments_DF = pd.DataFrame()


def plot_View_Duration(fig, df, row, column=1):
    """Return a graph object figure containing the view and a histogram of Duration in the specified row."""

    fig.add_trace(go.Scatter(x=df['Video_Num'],
                             y=df['viewCount'],
                             name='View Count',
                             line=dict(color='darkGreen', width=2)),
                  secondary_y=False,
                  row=row,
                  col=column)

    fig.add_trace(go.Bar(x=df['Video_Num'],
                         y=df['durationSecs'],
                         name='Duration in Sec.',
                         showlegend=True,
                         marker_color='blue',
                         marker_opacity=.5),
                  secondary_y=True,
                  row=row,
                  col=column)

    fig.update_yaxes(title_text='View Count', row=row,
                     col=column, secondary_y=False,)
    fig.update_yaxes(title_text='Duration in Sec.',
                     row=row, col=column, secondary_y=True,)

    return fig


def plot_Like_Comment(fig, df, row, column=1):
    """Return a graph object figure containing the like count and comment in the specified row."""

    fig.add_trace(go.Scatter(x=df['Video_Num'],
                             y=df['likeCount'],
                             name='Like Count',
                             line=dict(color='red', width=2)),
                  secondary_y=False,
                  row=row,
                  col=column)

    fig.add_trace(go.Bar(x=df['Video_Num'],
                         y=df['commentCount'],
                         name='Comment Count',
                         showlegend=True,
                         marker_opacity=.5),
                  secondary_y=True,
                  row=row,
                  col=column)

    fig.update_yaxes(title_text='Like Count', row=row,
                     col=column, secondary_y=False,)
    fig.update_yaxes(title_text='Comment Count', row=row,
                     col=column, secondary_y=True,)

    return fig


def plot_Ratio(df, Channel_Name):
    """Return a graph object figure containing the like to view, comment to view and comment to like % in the specified row."""
    ratio_data = []

    trace1 = go.Scatter(x=df['Video_Num'],
                        y=df['likeRatio'],
                        name='Like to View %',
                        mode='lines',
                        opacity=.8)
    ratio_data.append(trace1)

    trace2 = go.Scatter(x=df['Video_Num'],
                        y=df['commentRatio'],
                        name='Comment to View %',
                        mode='lines',
                        opacity=.8)
    ratio_data.append(trace2)

    trace3 = go.Scatter(x=df['Video_Num'],
                        y=df['commenttoLikePercent'],
                        name='Comment to Like %',
                        mode='lines',
                        opacity=.8)
    ratio_data.append(trace3)

    ratio_layout = go.Layout(
        title='Like to View, Comment to View and Comment to Like percent for {}'.format(
            Channel_Name),
        yaxis=dict(title='Viewer Engagement Metrics',
                   showline=True,
                   linecolor='black',
                   showgrid=True),
        xaxis=dict(title='Last 50 Uploaded Videos (50th most recent)',
                   showline=True,
                   linecolor='black',
                   showgrid=True),
        showlegend=True,
        hovermode='x unified',
        plot_bgcolor='white',
        legend=dict(
            bgcolor='white',
            bordercolor='black',
            orientation='v',
            x=.95,
            y=1.10,
            traceorder='normal',
            borderwidth=1)
    )

    fig = go.Figure(data=ratio_data, layout=ratio_layout)

    return fig


def blank_fig():
    '''This is added for aesthetic purpose. When the page loads, the div which contains the graph object blends with the background'''
    
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None, plot_bgcolor='rgba(245, 245, 245, 0.93)',
                      paper_bgcolor='rgba(245, 245, 245, 0.93)')
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig

youtube_channel_layout = html.Div([

    html.P("Enter or paste the YouTube video link below and click Submit button. The app will:"),
    html.Div([
        html.Li("Extract the channel name, total subscribers, and total views generated by the YouTube channel so far."),
        html.Li("Retrieve viewership activity and playtime duration for the latest 50 videos uploaded by the channel and display trends such as the ratio of likes to views, comments to views, and comments to likes."),
        html.Li("Display a word cloud of the most frequently used words in the comments section of the latest 50 videos uploaded by the channel."),
        html.Li("At the end, display a summary table of viewership metrics for the latest 50 videos uploaded on the channel."),
    ], className='app_task_list'),

    html.Label("Enter YouTube Channel URL:", className='label'),
    dcc.Input(id="youtube_url_channel",
              type="url",
              value='https://www.youtube.com/watch?v=ILgSesWMUEI',
              # placeholder="Example: https://www.youtube.com/watch?v=FkKPsLxgpuY&t=640s ",
              required=True,
              style={'marginRight': '10px'},
              persistence=False,
              className='input_box'),
    html.Br(),
    html.Button('Submit', id='submit-val', className='button', n_clicks=0),

    html.Br(),

    dcc.Loading(children=[

        html.Div(id='message'),

        html.Br(),
        html.Div([
            dcc.Graph(id='viewership_plot', figure=blank_fig(),
                      config={'displayModeBar': False}),
        ], className='graph_container'),
        html.Br(),
        html.Div([
            dcc.Graph(id='Ratio_plot', figure=blank_fig(),
                      config={'displayModeBar': False}),
        ], className='graph_container'),


        html.Div(id='wordcloud_figure_div', children=""),

        html.Div([
            html.P(id='summary_table_heading', className='response_title'),
            html.Div(id='youtube_channel_div'),
        ], className='large_table'),

        html.Br(),
    ], type="circle", fullscreen=True),

])

@app.callback(
    [Output('message', 'children'),
     Output('viewership_plot', 'figure'),
        Output('Ratio_plot', 'figure'),
        Output('wordcloud_figure_div', 'children'),
        Output('summary_table_heading', 'children'),
        Output('youtube_channel_div', 'children'),
        Output("youtube_url_channel", component_property='value')
     ],
    [Input('submit-val', 'n_clicks')],
    [State('youtube_url_channel', 'value')],
    prevent_initial_call=True
)
def app_layout(n_click, youtube_url):
   '''
   This Call back function performs following task:
   
   From the provided Youtube url, the video ID is extracted. 
   
   
   '''

    

    link = youtube_url
    print(link)

    pattern = 'v='
    message = ''
    match = re.search(pattern, link)
    # Checking whether the entered Youtube url has a video ID.
    if match == None:
        message = "Please check the YouTube Video url. It should be like 'https://www.youtube.com/watch?v=RywP7cCYUWE'  or like 'https://www.youtube.com/watch?v=FkKPsLxgpuY&t=648s' this. "

        print(message)
        message_div = html.Div([
            html.Div([], className='content_separator'),  # separator line
            html.H5([message], className='content_message')
        ])

        return message_div, blank_fig(), blank_fig(), '', [], [], ''
    else:
        vid_start = match.end()
        vid_end = vid_start+11
        video_id = link[vid_start:vid_end]
        print(video_id)

        # Getting Youtube Video Data (Channel ID)
        
        request = youtube.videos().list(
            part="snippet,statistics",
            id=video_id)

        response = request.execute()

        channel_ID = response['items'][0]['snippet']['channelId']

        # Getting Youtube Channel Data
        channel_data = []

        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=channel_ID)

        response = request.execute()

        # loop through response['items']. Extract relavent data for each item in dictionary and store the dictionary in List. 
        for item in response['items']:
            data = {'channelName': item['snippet']['title'],
                    'subscribers': item['statistics']['subscriberCount'],
                    'views': item['statistics']['viewCount'],
                    'totalVideos': item['statistics']['videoCount'],
                    'playlistId': item['contentDetails']['relatedPlaylists']['uploads']
                    }

            channel_data.append(data)

        print(channel_data)
        Channel_Name = channel_data[0]['channelName']
        subscribers = channel_data[0]['subscribers']
        views = channel_data[0]['views']
        totalVideos = channel_data[0]['totalVideos']
        playlistId = channel_data[0]['playlistId']

        # Getting the number in easy to read format Like 50 Million instead of 500000000
        subscribers1 = "{:,}".format(int(subscribers))
        views1 = "{:,}".format(int(views))
        totalVideos1 = "{:,}".format(int(totalVideos))

        message = f"The entererd Youtube url is {youtube_url} from '{Channel_Name}' Channel. As of today, {Channel_Name} has {subscribers1} ({numerize.numerize(int(subscribers))}) subscribers who have generated {views1} ({numerize.numerize(int(views))}) views from {totalVideos1} videos."

        message_div = html.Div([
            html.Div([], className='content_separator'),
            html.H6([message], className='content_message')
        ])

        # From playlistId get the video IDs recent 50 uploadeded videos of the channel

        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlistId,
            maxResults=50)
        response = request.execute()

        video_ids = []

        for i in range(len(response['items'])):
            video_ids.append(response['items'][i]['contentDetails']['videoId'])

        # Getting Video Info like, number of views, etc.

        all_video_info = []

        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_ids
        )
        response = request.execute()

        for video in response['items']:   #video is a nested dictionary/list object provided by Youtube.
            stats_to_keep = {'snippet': ['channelTitle', 'title', 'publishedAt'],
                             'statistics': ['viewCount', 'likeCount', 'commentCount'],
                             'contentDetails': ['duration']
                             }
            video_info = {}  # For storing extracted data in dictionary.
            video_info['video_id'] = video['id']

            for k in stats_to_keep.keys():  # This will generate a list ['snippet','statistics','contentDetails']
                for v in stats_to_keep[k]:  
                    try:
                        video_info[v] = video[k][v]
                    except:
                        video_info[v] = None

            all_video_info.append(video_info)

        all_video_info_DF = pd.DataFrame(all_video_info)  # Convert list of dictionary to Dataframe

        # Reformating the published time:
        all_video_info_DF['publishedAt'] = all_video_info_DF['publishedAt'].apply(
            lambda x: parser.parse(x))
        all_video_info_DF['publishedAt'] = pd.to_datetime(
            all_video_info_DF['publishedAt'])
        all_video_info_DF['publishedAt'] = all_video_info_DF['publishedAt'].apply(
            lambda x: x.strftime('%Y-%m-%d'))

        # convert duration to seconds
        all_video_info_DF['durationSecs'] = all_video_info_DF['duration'].apply(
            lambda x: pd.Timedelta(x))
        all_video_info_DF['durationSecs'] = all_video_info_DF['durationSecs'].apply(
            lambda x: pd.Timedelta.total_seconds(x))
        all_video_info_DF['durationSecs'] = all_video_info_DF['durationSecs'].apply(
            lambda x: int(x))

        # Converting numeric columns to numeric data type
        cols = ['viewCount', 'likeCount', 'commentCount']
        all_video_info_DF[cols] = all_video_info_DF[cols].apply(
            pd.to_numeric, errors='coerce', axis=1)

        # Getting like to view and comment to view ratio:
        all_video_info_DF['likeRatio'] = all_video_info_DF['likeCount'] / \
            all_video_info_DF['viewCount'] * 100
        all_video_info_DF['commentRatio'] = all_video_info_DF['commentCount'] / \
            all_video_info_DF['viewCount'] * 100
        all_video_info_DF['likeRatio'] = all_video_info_DF['likeRatio'].round(
            2)
        all_video_info_DF['commentRatio'] = all_video_info_DF['commentRatio'].round(
            2)

        all_video_info_DF['commenttoLikePercent'] = all_video_info_DF['commentCount'] / \
            all_video_info_DF['likeCount'] * 100
        all_video_info_DF['commenttoLikePercent'] = all_video_info_DF['commenttoLikePercent'].round(
            2)

        all_video_info_DF["Video_Num"] = np.arange(
            1, len(all_video_info_DF) + 1)
        all_video_info_DF["Video_Num"] = all_video_info_DF['Video_Num'].apply(
            lambda x: ((x-51)*-1))
        print(all_video_info_DF)

        # Getting top 5 comments for each video uploaded

        all_comments = []
        for video_id in video_ids:
            try:
                request = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=5)    # For each video, only 5 comments are extracted.
                response = request.execute()
                comments_in_video = [comment['snippet']['topLevelComment']
                                     ['snippet']['textOriginal'] for comment in response['items'][0:5]]
                comments_in_video_info = {
                    'video_id': video_id, 'comments': comments_in_video}
                all_comments.append(comments_in_video_info)

            except:
                # When error occurs - most likely because comments are disabled on a video
                # print('Could not get comments for video ' + video_id)
                comments_in_video_info = {
                    'video_id': video_id, 'comments': 'Could not get comments for video '}
                all_comments.append(comments_in_video_info)

        all_comments_DF = pd.DataFrame(all_comments)

        # Plotting the metrics
        fig = make_subplots(rows=2,
                            cols=1,
                            specs=[[{"secondary_y": True}],
                                   [{"secondary_y": True}]],
                            shared_xaxes=True,
                            vertical_spacing=0.08,
                            row_width=[0.2, 0.3])

        fig = plot_View_Duration(fig, all_video_info_DF, row=1)
        fig = plot_Like_Comment(fig, all_video_info_DF, row=2)
        fig.update_xaxes(title_text='Recent 50 Uploaded Videos latest->',
                         showline=True,
                         linecolor='black',
                         showgrid=True)
        fig.update_yaxes(
            showline=True,
            linecolor='black',
            showgrid=True)

        fig.update_layout(

            title='Viewership Metrices for {}'.format(Channel_Name),
            showlegend=True,
            hovermode='x unified',
            plot_bgcolor='white',
            legend=dict(
                      bgcolor='white',
                      bordercolor='black',
                      orientation='v',
                      x=.95,
                y=1.16,
                      traceorder='normal',
                      borderwidth=1)
        )

        fig1 = plot_Ratio(all_video_info_DF, Channel_Name)
        

        all_comments_DF['comments_no_stopwords'] = all_comments_DF['comments'].apply(
            lambda x: [item for item in str(x).split() if item not in stopwords])

        all_words = list(
            [a for b in all_comments_DF['comments_no_stopwords'].tolist() for a in b])
        all_words_str = ' '.join(all_words)

        my_wordcloud = WordCloud(width=2420, height=1500, random_state=1, background_color='black',
                                 colormap='viridis', collocations=False).generate(all_words_str)

        # visualize wordcloud inside plotly figure
        fig2 = px.imshow(my_wordcloud, template='ggplot2')
        fig2.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        fig2.update_xaxes(visible=False)
        fig2.update_yaxes(visible=False)

        wordcloud_Fig = html.Div([
            html.P(["WordCloud for the recent few comments recieved by channel '{}':".format(
                Channel_Name)], className='response_title'),
            dcc.Graph(figure=fig2, config={"displayModeBar": False}, style={
                'width': '92%', 'height': '74vh'})

        ], className='graph_container')

        # Summary Table
        summary_table = all_video_info_DF[[
            'publishedAt', 'title', 'viewCount', 'likeCount', 'duration']]
        summary_table.rename(columns={'publishedAt': 'Published On', 'title': 'Video Title', 'viewCount': 'View Count',
                                      'likeCount': 'Like Count', 'duration': 'Duration'}, inplace=True)

        print(summary_table.head(10))

        summary_table_heading = "'{}' Youtube channel summary for the recent 50 videos uploaded:".format(
            Channel_Name)

        youtube_channel_table = dash_table.DataTable(id='summary_table',
                                                     cell_selectable=False,
                                                     data=summary_table.to_dict(
                                                         orient='records'),
                                                     columns=[{'name': col, 'id': col}
                                                              for col in summary_table.columns],
                                                     page_action="native",
                                                     page_current=0,
                                                     page_size=25,
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
                                                             'if': {'column_id': 'Published On'},
                                                             'width': '25px',
                                                             'textAlign': 'center'
                                                         },
                                                         {
                                                             'if': {'column_id': 'Video Title'},
                                                             'maxWidth': '150px',
                                                             'textAlign': 'left',
                                                             'textOverflow': 'ellipsis',
                                                             'padding-left': '8px',

                                                         },
                                                         {
                                                             'if': {'column_id': 'View Count'},
                                                             'width': '25px',
                                                             'textAlign': 'center'
                                                         },
                                                         {
                                                             'if': {'column_id': 'Like Count'},
                                                             'width': '25px',
                                                             'textAlign': 'center'
                                                         },
                                                         {
                                                             'if': {'column_id': 'Duration'},
                                                             'width': '25px',
                                                             'textAlign': 'center'
                                                         },

                                                     ]


                                                     ),

        return message_div, fig, fig1, wordcloud_Fig,  summary_table_heading, youtube_channel_table, ''
