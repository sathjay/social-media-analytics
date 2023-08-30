import dash
import dash_bootstrap_components as dbc

metaTags = [
    {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}]

external_stylesheets = [metaTags, dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, meta_tags=metaTags, external_stylesheets=external_stylesheets, title='Social-Media-Analytics',
                suppress_callback_exceptions=True)

server = app.server
