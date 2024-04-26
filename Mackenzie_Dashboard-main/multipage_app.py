import dash


app = dash.Dash(__name__,
    suppress_callback_exceptions=True,
    external_stylesheets=['https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/cosmo/bootstrap.min.css'],
    # meta_tags=[
    #     {
    #         'name': 'viewport',
    #         'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'
    #     }
    # ],
    )
server = app.server
app.title='Mackenzie River Monitoring'
