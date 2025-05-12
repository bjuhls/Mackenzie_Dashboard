import dash
#import dash_core_components as dcc
#import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from multipage_app import app
from multipage_app import server
from layouts import main_page, team_page, navbar, imprint_page, accessibility_page
import callbacks

# import dash_auth


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
    #if pathname == '/Mackenzie':
         return main_page
    if pathname == '/team':
    #if pathname == '/Mackenzie/team':
         # auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
         return team_page
    if pathname == '/imprint':
    #if pathname == '/Mackenzie/team':
         # auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
         return imprint_page
    if pathname == '/accessibility':
    #if pathname == '/Mackenzie/team':
         # auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
         return accessibility_page
    else:
        return html.Div([
            html.P(
                [
                    '404: Page not found. ',
                    html.A('Return to main page',
                        href='/',
                        style={'color':'darkblue'}
                    )
                ]
            )
        ])

if __name__ == '__main__':
    app.run(debug=True)
