import dash
from dash import dcc
from dash import html

from app import app

home_LO = html.Div([



    html.H3(["Welcome to Social-MediaAnaytics.com: "], className='home_title'),
    html.P(["This website was created to demonstrate how Python can be used to collect data from social media platforms via APIs, such as those of YouTube and Reddit. It also showcases how this data can be analyzed using ChatGPT and NLP, and subsequently visualized with Plotly and Dash. The code for this website is available on my GitHub page, with the link located in the 'About Me' section. Please navigate to the tabs above to explore further."], className='home_text'),



], className='LO_container')
