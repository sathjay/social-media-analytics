import dash
from dash import dcc
from dash import html

from app import app

about_me_LO = html.Div([


    html.H3(["About Me:"], className='home_title'),
    html.P(["I am Sathya Jayagopi, a seasoned Software Developer with over 12 years of experience spanning Software Development and Test Management. Over the last year, with the rollout of ChatGPT, tremendous progress has been made in Large Language Models (LLMs) and Natural Language Processing. As a tech enthusiast and lifelong learner, I'm always on the hunt for the latest advancements in the ever-evolving landscape of technology. My passion lies in crafting Interactive Data Analytic web applications, which led me to build this app."], className='home_text'),

    html.P([html.A("LinkedIn", href='https://www.linkedin.com/in/sathya-jayagopi/',
           target='_blank', className='libutton')], className='home_text'),

    html.P([html.A("GitHub", href='https://github.com/sathjay?tab=repositories',
           target='_blank', className='libutton')], className='home_text'),


], className='LO_container')
