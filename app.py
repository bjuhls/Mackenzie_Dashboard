import dash
from dash import Dash
from dash import dcc
from dash import html
#import dash_bootstrap_components as dbc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context
import dash_table
from dash_table.Format import Format, Align
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import xlsxwriter
from scipy.stats import linregress
from scipy.optimize import curve_fit


# import data
df = pd.read_csv('data/PublishedLenaMonitoringData.csv', parse_dates=['DateTime'])
df['Day of Year'] = df.DateTime.dt.dayofyear
df['Year'] = df.DateTime.dt.year
df['Month'] = df.DateTime.dt.month
# df['x_artificial'] = np.linspace(1, 10, df.shape[0])
# df['logy_artificial'] = 4 * np.log(df.x_artificial) - 2 + np.random.normal(size=df.shape[0])
# df['powy_artificial'] = 2 * np.power(df.x_artificial, 2.5) + 4 + np.random.normal(size=df.shape[0])*50

dis = pd.read_csv('data/Lena_Kyusyur_1936_2020_corrected_20230807.csv',
    parse_dates=['Datetime Samoylov'], index_col='Datetime Samoylov', sep=';'
)
df['Discharge'] = dis.loc[list(df.Date)].discharge.values

param_info = pd.read_csv('data/parameter_information.csv', index_col='Name')

# df.iloc[0, :].to_csv('parameter_information_empty.csv')

# define columns to use
not_used = set()
remove_str = ['ID', 'QF', 'cations and anions', 'cuvette lenght', 'Instrument']
for c in df.columns:
    for r in remove_str:
        if r in c:
            not_used.add(c)
used_cols = sorted([col for col in df.columns if col not in not_used], key=str.casefold)

# define colors
clinfit = 'royalblue'
clogfit = 'green'
cpowfit = 'firebrick'
theme = '#3d837f'
theme_second = '#dbe7f5'
muted_blue = 'royalblue'
brick_red = 'crimson'
darklink = '#373a3c'

app = Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/cosmo/bootstrap.min.css'])
server = app.server
app.title='Lena River Monitoring'

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Time Series", href="#time-series", external_link=True)),
        dbc.NavItem(dbc.NavLink("Scatter", href="#scatter", external_link=True)),
        dbc.NavItem(dbc.NavLink("Gallery", href="#gallery", external_link=True)),
        dbc.NavItem(dbc.NavLink("Download", href="#download", external_link=True)),
        dbc.NavItem(dbc.NavLink("Read more", href="#read-more", external_link=True)),
        dbc.NavItem(dbc.NavLink("Team", href="", external_link=True, disabled=True)),
        # dbc.NavItem(dbc.NavLink(html.A("\U00002709 lena.monitoring@awi.de", href="mailto:lena.monitoring@awi.de"))),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Email", header=True),
                dbc.DropdownMenuItem(html.A("\U00002709 lena.monitoring@awi.de", href="mailto:lena.monitoring@awi.de", style={'color':darklink}),)
            ],
            nav=True,
            in_navbar=True,
            label="Contact",
        ),
    ],
    # brand="Home",
    brand_href="#",
    color=theme,
    dark=True,
    sticky='top',
    fixed='top'
)

app.layout = dbc.Container([
    navbar,
    dbc.Container(
        dbc.Row([
            dbc.Col(
                html.Img(src='assets/LenaMonitoringLogo_2row_white.png', width='100%'),
                width=3,
                xl=3, lg=3, md=3, sm=2, xs=2
            ),
            dbc.Col(
                [
                    html.H1(
                        [
                            "Monitoring of the Lena River Biogeochemistry",
                            html.Br(),
                            "at the Samoylov Island Research Station"
                        ],
                         className='header-title',
                         style={'font-size': '32px'}
                    ),
                    html.P(
                        children=[
                            # 'Welcome to the Lena River Monitoring dashboard.', html.Br(),
                            ' This interactive dashboard gives you the opportunity'
                            ' to explore data from the Samoylov research station',
                            html.Br(),
                            ' in Siberia, Russia.'
                        ],
                        className='header-description',
                    ),

                ],
                align='center',
                # width=8
                xl=8, lg=8, md=12, sm=12, xs=12,
            ),
        ],
        justify='center'
        ),
        className='header',
    ),
    # navbar,

    # time series plot
    dbc.Card(id='time-series', children=[
        dbc.CardHeader(html.H4('Explore the Time Series'), id='explore'),
        dbc.Row([
            dbc.Col(
                [
                    dbc.Row([
                    dbc.Col(html.P('Select first y-value', className='menu-title'),
                        # width=8,
                        xl=8, lg=12, md=8, sm=8, xs=8,
                    ),
                    dbc.Col(dcc.Checklist(
                        id='y1-log',
                        options=[{'label': ' log scale', 'value': 'on'}],
                        value=[],
                        style={},
                        className='menu-title'
                    ))
                    ], align='bottom', justify='between', no_gutters=True),
                    dcc.Dropdown(
                        id='first_y',
                        options=[
                            {'label': l, 'value': l} for l in used_cols
                        ],
                        multi=False,
                        style={'width': '100%'},
                        value='Discharge',
                        className='dropdown',
                    ),
                    dbc.Row([
                    dbc.Col(html.P('Select second y-value', className='menu-title'),
                        # width=8,
                        xl=8, lg=12, md=8, sm=8, xs=8,
                    ),
                    dbc.Col(dcc.Checklist(
                        id='y2-log',
                        options=[{'label': ' log scale', 'value': 'on'}],
                        value=[],
                        className='menu-title'
                    ))
                    ], align='bottom', justify='between', no_gutters=True),
                    dcc.Dropdown(
                        id='second_y',
                        options=[
                            # {'label': l, 'value': l} for l in sorted(df.columns[6:], key=str.casefold)
                            {'label': l, 'value': l} for l in used_cols
                        ],
                        multi=False,
                        style={'width': '100%'},
                        value='Conductivity lab (µS/cm)',
                        className='dropdown',
                    ),
                    html.P('Select Time Window', className='menu-title'),
                    dcc.DatePickerRange(
                        id='time-series-date-range',
                        min_date_allowed=df.DateTime.min().date(),
                        max_date_allowed=df.DateTime.max().date(),
                        start_date=df.DateTime.min().date(),
                        end_date=df.DateTime.max().date(),
                        display_format='DD.MM.YYYY',
                        className='dropdown',
                        style={'width': '100%'},
                    ),
                    html.Div(style={'margin-top': '24px'}),
                    html.Button(
                        "Show parameter information",
                        id="collapse-button",
                        className="btn btn-primary, button",
                        # color="primary",
                        n_clicks=0,
                    ),
                ],
                # width=3,
                xl=3, lg=3, md=6, sm=8, xs=10,
                align='center'
                ),
            # dbc.Col()
            dbc.Col(
                [
                    dcc.Graph(
                        id='time-series-plot',
                    )
                ],
                xl=8, lg=8, md=10, sm=12, xs=12,
            )
        ],
        justify='around',),

        # dbc.Row(
        dbc.Collapse(
            dbc.Row(
                children=[
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.P(id='y1-param', style={'font-weight': 'bold', 'color':muted_blue}),
                                html.P(id='y1-info',
                                    className='text'
                                ),
                            ]),
                            color='primary',
                            outline=True,
                        ),
                        xl=5, lg=5, md=10, sm=11, xs=11,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.P(id='y2-param', style={'font-weight': 'bold', 'color':brick_red}),
                                html.P(id='y2-info',
                                    className='text'
                                ),
                            ],
                            # className='info-card'
                            ),
                            color='danger',
                            outline=True,
                        ),
                        xl=5, lg=5, md=10, sm=11, xs=11,
                    ),
                ],
                justify='center',
                style={
                    'margin-bottom':'36px',
                    'margin-top':'-12px',
                    }
            ),
            id="collapse",
            is_open=False,
        )
        # )
        # dbc.Row(
        #     children=[dbc.Collapse(children=[
        #         dbc.Row([
        #         dbc.Col(
        #             dbc.Card(
        #                 dbc.CardBody("This content is hidden in the collapse")
        #             ),
        #             xl=12, lg=3, md=6, sm=8, xs=10,
        #         ),
        #         dbc.Col(
        #             dbc.Card(
        #                 dbc.CardBody("This content is hidden in the collapse")
        #             ),
        #             xl=6, lg=6, md=6, sm=8, xs=10,
        #         ),]
        #         ),],
        #     id="collapse",
        #     is_open=True,
        #     ),
        #     ],
        #     # justify='around'
        # ),
    ]),


    # scatter plot
    dbc.Card(id='scatter', children=[
        dbc.CardHeader(html.H4('Check for correlations between parameter')),
        dbc.Row([
            dbc.Col(
                [
                    dbc.Row([
                    dbc.Col(html.P('Select x-value', className='menu-title'),
                        width=8,
                        xl=8, lg=12, md=8, sm=8, xs=8,
                    ),
                    dbc.Col(dcc.Checklist(
                        id='x-log',
                        options=[{'label': ' log scale', 'value': 'on'}],
                        value=[],
                        className='menu-title'
                    ))
                    ], align='bottom', justify='between', no_gutters=True),
                    dcc.Dropdown(
                        id='x_selected',
                        options=[
                            {'label': l, 'value': l} for l in used_cols
                        ],
                        multi=False,
                        style={'width': '100%'},
                        value='d18O (o/oo) vs. SMOW',
                        # value = 'Temperature (°C)',
                        # value = 'Conductivity lab (µS/cm)',
                        className='dropdown',

                        ),
                    dbc.Row([
                    dbc.Col(html.P('Select y-value', className='menu-title'),
                        width=8,
                        xl=8, lg=12, md=8, sm=8, xs=8,
                    ),
                    dbc.Col(dcc.Checklist(
                        id='y-log',
                        options=[{'label': ' log scale', 'value': 'on'}],
                        value=[],
                        className='menu-title'
                    ))
                    ], align='bottom', justify='between', no_gutters=True),
                    dcc.Dropdown(
                        id='y_selected',
                        options=[
                            {'label': l, 'value': l} for l in used_cols
                        ],
                        multi=False,
                        style={'width': '100%'},
                        value='dD (o/oo) vs. SMOW',
                        # value = 'Temperature (°C)',
                        # value = 'logy_artificial',
                        # value = 'Conductivity in situ (µS/cm)',
                        className='dropdown',
                    ),
                    dbc.Row([
                    dbc.Col(html.P('Select color', className='menu-title'),
                        width=8,
                        xl=8, lg=12, md=8, sm=8, xs=8,
                    ),
                    dbc.Col(dcc.Checklist(
                        id='color-log',
                        options=[{'label': ' log scale', 'value': 'on'}],
                        value=[],
                        className='menu-title'
                    ))
                    ], align='bottom', justify='between', no_gutters=True),
                    dcc.Dropdown(
                        id='color_selected',
                        options=[
                            # {'label': l, 'value': l} for l in sorted(df.columns[6:], key=str.casefold)
                            {'label': l, 'value': l} for l in used_cols
                        ],
                        multi=False,
                        style={'width': '100%'},
                        # value='Day of Year',
                        value = 'Temperature (°C)',
                        className='dropdown',
                    ),
                    html.P('Select Time Window', className='menu-title'),
                    dcc.DatePickerRange(
                        id='scatter-plot-date-range',
                        min_date_allowed=df.DateTime.min().date(),
                        max_date_allowed=df.DateTime.max().date(),
                        start_date=df.DateTime.min().date(),
                        end_date=df.DateTime.max().date(),
                        display_format='DD.MM.YYYY',
                        className='dropdown',
                        style={'width': '100%'},
                    ),
                    html.P('Select Fit', className='menu-title'),
                    dcc.Checklist(
                        id='linear-fit',
                        options=[{'label': ' show linear fit', 'value': 'on'}],
                        value=[],
                    ),
                    dcc.Checklist(
                        id='log-fit',
                        options=[{'label': ' show logarithmic fit', 'value': 'on', 'disabled': False}],
                        value=[],
                    ),
                    dcc.Checklist(
                        id='power-fit',
                        options=[{'label': ' show power fit', 'value': 'on', 'disabled': False}],
                        value=[],
                    )
                ],
                # width=3,
                xl=3, lg=3, md=6, sm=8, xs=10,
                align='center',
                style={'margin-bottom': '24px'},
                ),


            dbc.Col(
                [
                    dcc.Graph(
                        id='scatter-plot',
                        style={'margin-bottom': '-20px'},
                    ),
                    dbc.Row(
                    # dbc.CardDeck(id='text-output'),                                  # this row holds the 'fitcards'
                    id='text-output',
                    justify='center',
                    style={'margin-bottom': '30px'},
                    )
                ],
                # width=8
                xl=8, lg=8, md=10, sm=12, xs=12,
            )
            ],
            justify='around',
        ),
        # dbc.Row([
        #     dbc.Col(
        #         [
                    # html.P('Select Fit', className='menu-title'),
                    # dcc.Checklist(
                    #     id='linear-fit',
                    #     options=[{'label': ' show linear fit', 'value': 'on'}],
                    #     value=[],
                    # ),
                    # dcc.Checklist(
                    #     id='log-fit',
                    #     options=[{'label': ' show logarithmic fit', 'value': 'on', 'disabled': False}],
                    #     value=[],
                    # ),
                    # dcc.Checklist(
                    #     id='power-fit',
                    #     options=[{'label': ' show power fit', 'value': 'on', 'disabled': False}],
                    #     value=[],
                    # )
                # ],
                # width=3,
                # xl=3, lg=3, md=6, sm=8, xs=10,
            # ),
            # dbc.Col(
            #     [
            #         dbc.Row(
            #         # dbc.CardDeck(id='text-output'),                                  # this row holds the 'fitcards'
            #         id='text-output',
            #         justify='center',
            #         style={'margin-bottom': '20px'},
            #         )
            #     ],
            #     # width=8,
            #     xl=8, lg=8, md=11, sm=11, xs=11
            # )
        # ],
        # align='start',
        # justify='around',
        # style={'margin-top':'-0px', 'margin-bottom': '12px'}
        # )
    ]),

    # Slideshow
    dbc.Card(id='gallery',
        children=[
            dbc.CardHeader(html.H4('Get impressions from the field work')),
            # dbc.CardImg(id='img-slide', src="assets/slideshow1.png", top=True, className='center-block, slideshow-image'),
            dbc.CardBody([
                dbc.Row(
                    # dbc.Col(
                        dbc.CardImg(id='img-slide', src="assets/slideshow1.png", top=True, className='center-block, slideshow-image'),
                        # width=12
                        # ),
                justify='center',
                ),
                html.Div(style={'margin-top':'24px'}),
                dbc.Row([
                    dbc.Col(
                        dbc.Row(html.Button("\U0000276E", id="btn_prev", className="btn btn-primary, button"), justify='start'),
                        xl=1, lg=1, md=1, sm=2, xs=3),
                    dbc.Col(
                        children=[
                            dbc.Row(
                                html.P('This example image shows a part of the Lena Delta in bright colors.',
                                    id='img-description',
                                    className='text',
                                    style={'text-align': 'center'}
                                ),
                            justify='center'),
                            # html.P(id='image-counter')
                        ],
                        xl=8, lg=8, md=8, sm=8, xs=6),
                    dbc.Col(
                        dbc.Row(html.Button("\U0000276F", id="btn_next", className="btn btn-primary, button"), justify='end'),
                        xl=1, lg=1, md=1, sm=2, xs=3),
                ],
                justify='around',
                align='center'
                )
            ])
        ]
    ),





    # Download section
    dbc.Card(id='download',
        children=[
            dbc.CardHeader(html.H4('Download the dataset to expand your analysis')),#, className='card-header'),
            dbc.CardBody(
                [
                    # html.H4('Download section', style={'text-align':'center'}),
                    dbc.Row(html.P('Choose your data',
                        style={'font-weight': 'bold',
                            'font-size': '18px',
                            'text-align': 'center',
                            'margin-top': '10px',
                            'margin-bottom': '10px'}),
                        style={'justify-content':'center'},
                    ),
                    dbc.Row([
                        # dbc.Col(dbc.Row(html.P('1.'), style={'justify-content':'center'},),
                        #     width=1,
                        #     xl=1, lg=1, md=3, sm=2, xs=1
                        # ),
                        dbc.Col(
                            [
                                html.P('\U000027A4 Select Parameter', className='menu-title'),
                                dcc.Dropdown(
                                    id='download-parameter',
                                    options=[
                                        {'label': l, 'value': l} for l in sorted(df.columns, key=str.casefold)
                                    ],
                                    multi=True,
                                    # value=['Temperature (°C)', 'Conductivity in situ (µS/cm)']
                                ),
                            ],
                            # width=3,
                            xl=3, lg=3, md=7, sm=8, xs=10
                        ),
                        # dbc.Col(dbc.Row(html.P('2.'), style={'justify-content':'center'},),
                        #     # width=1,
                        #     xl=1, lg=1, md=3, sm=2, xs=1
                        #     ),
                        dbc.Col(
                            [
                                html.P('\U000027A4 Select Time Window', className='menu-title'), #\U0001F447
                                dcc.DatePickerRange(
                                    id='download-date-range',
                                    min_date_allowed=df.DateTime.min().date(),
                                    max_date_allowed=df.DateTime.max().date(),
                                    start_date=df.DateTime.min().date(),
                                    end_date=df.DateTime.max().date(),
                                    display_format='DD.MM.YYYY',
                                    className='dropdown',
                                    style={'width': '100%'},
                               ),
                            ],
                            # width=4
                            xl=4, lg=5, md=7, sm=8, xs=10
                        ),
                        # dbc.Col(dbc.Row(html.P('3.'), style={'justify-content':'center'},),
                        #     # width=1,
                        #     xl=1, lg=1, md=3, sm=2, xs=1
                        # ),
                        dbc.Col(
                            [
                                html.P('\U000027A4 Download Data', className='menu-title'),
                                dbc.Row([
                                html.Div(style={'margin-right': '15px'}),
                                html.Button("CSV", id="btn_csv", className="btn btn-primary, button"),
                                dcc.Download(id="download-dataframe-csv"),
                                html.Div(style={'margin-right': '10px'}),
                                html.Button("Excel", id="btn_xlxs", className="btn btn-primary, button"),
                                dcc.Download(id="download-dataframe-xlxs"),
                                ])
                                # html.Button("\U000027A4 Download CSV", id="btn_csv", className="btn btn-primary, button"),
                                # dcc.Download(id="download-dataframe-csv"),
                                # html.Div(style={'margin-top': '10px'}),
                                # html.Button(" \U000027A4 Download Excel", id="btn_xlxs", className="btn btn-primary, button"),
                                # dcc.Download(id="download-dataframe-xlxs"),
                            ],
                            style={'justify-content':'start', 'margin-top': '0px'},
                            # width=2,
                            xl=2, lg=2, md=7, sm=8, xs=10,
                            align='start'

                        ),
                    ],
                    # style={
                    #     'justify-content': 'start',
                    #     # 'margin': '8px, 100px, 50px, auto'
                    # },
                    justify='around',
                    # align='start'
                    ),
                    dbc.Row(html.P('OR',
                        style={'font-weight': 'bold',
                            'font-size': '18px',
                            'text-align': 'center',
                            'margin-top': '20px',
                            'margin-bottom': '20px'}),
                        style={'justify-content':'center'},
                    ),
                    dbc.Row(
                        # dbc.Col(
                            [
                                html.P('Download full dataset:', className='menu-title'),
                                html.Div(style={'margin-left': '40px'}),
                                html.Button("Download CSV", id="btn_csv_full", className="btn btn-primary, button"),
                                dcc.Download(id="download-dataframe-csv_full"),
                                html.Div(style={'margin-left': '10px'}),
                                html.Button("Download Excel", id="btn_xlxs_full", className="btn btn-primary, button"),
                                dcc.Download(id="download-dataframe-xlxs_full"),
                            ],
                        # )
                        style={'justify-content': 'center'}
                    ),
                    html.Div(style={'margin-top': '48px'}),
                    dbc.Row([
                        html.P([
                            'Please cite any use of the data as indicated below. For more information and additional datasets feel free to visit the ',
                            html.A('Pangaea Homepage', href='https://www.pangaea.de/', target="_blank"),
                            '.',
                            ],
                            style={'text-align':'center', 'width':'90%'},
                            className='text'
                            ),
                        ],
                        justify='center'
                    ),
                    html.Div(style={'margin-top': '24px'}),
                    dbc.Row(
                        html.P(
                            [
                                'Juhls, B; Morgenstern, A; Chetverova, A et al. (2020): Temperature, electrical conductivity, DOC, CDOM, stable water isotopes',
                                ' and major ions of Lena River water from April 2018 to April 2019. ',
                                html.A(' https://doi.org/10.1594/PANGAEA.913196', href='https://doi.org/10.1594/PANGAEA.913196', target="_blank")
                            ],
                            className='text',
                            style={'text-align':'center', 'width':'80%'}),
                        justify='center')
                ],
        # style={'margin': '8px, 100px, 50px, auto'}
            )
        ]
    ),

    # Publications and Partners
    dbc.Card(id='read-more', children=[
        dbc.CardHeader(html.H4('Read more')),
        dbc.CardBody(
            children=[
                dbc.Row([
                    # Arctic Gro
                    dbc.Col(
                        dcc.Link(
                        dbc.Card([
                            dbc.CardImg(src="assets/ArcticGreatRiversObservatory.png", top=True, className='preview-image'),
                            dbc.CardBody([
                                html.P(
                                    "Visit the Arctic Great Rivers Observatory",
                                    className="text",
                                    )
                            ]),
                        ],
                        ), # end of card
                        href='https://arcticgreatrivers.org/',
                        target="_blank",
                        style={'color':darklink}
                        ),
                    xl=6, lg=6, md=10, sm=12, xs=12
                    ), # end of col

                    # Juhls et al. 2020
                    dbc.Col(
                        dcc.Link(
                        dbc.Card([
                            dbc.CardImg(src="assets/juhls_etal_preview.jpg", top=True, className='preview-image'),
                            dbc.CardBody([
                                html.P(
                                    "Learn about Drivers of Seasonality and Dissolved Organic Matter Fluxes",
                                    className="text",
                                    )
                            ]),
                        ],
                        ), # end of card
                        href='https://doi.org/10.3389/fenvs.2020.00053',
                        target="_blank",
                        style={'color':darklink}
                        ),
                    xl=6, lg=6, md=10, sm=12, xs=12
                    ) # end of col

                ],
                justify='around'
                ) # end of row
            ]
        ) # end of card body
    ]),


    #     dbc.CardBody(
    #     [
    #         html.H4('Publications'),
    #         html.Ul([html.Li(i) for i in
    #             [
    #                 [
    #                     'Juhls B, Stedmon CA, Morgenstern A, Meyer H, Hölemann J, Heim B, Povazhnyi V and Overduin PP (2020) Identifying Drivers of Seasonality in Lena River Biogeochemistry and Dissolved Organic Matter Fluxes. Front. Environ. Sci. 8:53. ',
    #                     html.A('https://doi.org/10.3389/fenvs.2020.00053',
    #                     href='https://doi.org/10.3389/fenvs.2020.00053', target="_blank", style={'font-color': 'black'})
    #                 ],
    #                 [
    #                     'Shiklomanov A. et al. (2021) River Freshwater Flux to the Arctic Ocean. In: Yang D., Kane D.L. (eds) Arctic Hydrology, Permafrost and Ecosystems. Springer, Cham. ',
    #                     html.A('https://doi.org/10.1007/978-3-030-50930-9_24',
    #                     href='https://doi.org/10.1007/978-3-030-50930-9_24', target="_blank", style={'font-color': 'black'}),
    #                 ],
    #                 '...'
    #             ]
    #         ]),
    # #     ],
    # #     # style={'margin-bottom': '20px', 'margin-left': '10px'}
    # # )),
    # #
    # # dbc.Card(dbc.CardBody(
    # #     [
    #         html.H4('Partners'),
    #         html.Ul([html.Li(i) for i in
    #             [
    #                 'C.A. Stedmon (DTU)',
    #                 '...'
    #             ]
    #         ]),
    #     ],
    #     style={'margin-bottom': '20px', 'margin-left': '10px'}
    # )]),


    # footer
    dbc.Container(
        [
            dbc.Row([
                dbc.Col(
                    html.A(
                        html.Img(
                            src='assets/1200px-AWI_Logo_2017.svg.png',
                            style={'height': '50px'},
                            title='Alfred Wegener Institute (AWI)'),
                        href='https://www.awi.de/en/',
                        target="_blank"
                        ),
                    width=1
                ),
                dbc.Col(
                    html.A(
                        html.Img(src='assets/LogoOtto.gif',
                            style={'height': '50px'},
                            title='Otto Schmidt Laboratory (OSL)'),
                        href='https://www.otto-schmidt-laboratory.de/en',
                        target="_blank"
                        ),
                    width=1
                ),
                dbc.Col(
                    html.A(
                        html.Img(src='assets/IPGG.png',
                            style={'height': '50px'},
                            title='Trofimuk Institute of Petroleum Geology and Geophysics (IPGG)'),
                        href='http://www.ipgg.sbras.ru/en',
                        target="_blank"
                        ),
                    width=1
                ),dbc.Col(
                    html.A(
                        html.Img(src='assets/logoaari.png',
                            style={'height': '50px'},
                            title='Arctic and Antarctic Research Institute (AARI)'),
                        href='http://www.aari.ru/main.php?lg=1&id=54',
                        target="_blank"
                        ),
                    width=1
                ),
                # dbc.Col(
                #     html.Img(src='assets/IPGG.png',
                #         style={'height': '50px'}),
                #         width=1
                # ),
                # dbc.Col(
                #     html.Img(src='assets/logoaari.png',
                #         style={'height': '50px'}),
                #         width=1
                # ),
            ],
            justify='around'),
        ],
        className='footer'
    )



])

# Time series plot
@app.callback(
    [
        Output(component_id='time-series-plot', component_property='figure'),
        Output('y1-log', 'style'),
        Output('y2-log', 'style'),
        Output('y1-param', 'children'),
        Output('y2-param', 'children'),
        Output('y1-info', 'children'),
        Output('y2-info', 'children')
    ],
    [
        Input('first_y', 'value'),
        Input('second_y', 'value'),
        Input('time-series-date-range', 'start_date'),
        Input('time-series-date-range', 'end_date'),
        Input('y1-log', 'value'),
        Input('y2-log', 'value')
    ]
)

def update_time_series_plot(first_y, second_y, start, end, y1log, y2log):

    # get param info
    y1_info = param_info.loc[first_y, 'comment']
    y2_info = param_info.loc[second_y, 'comment']

    # handle data
    data = df.copy()
    time_mask = (data.DateTime.dt.date >= pd.to_datetime(start)) & (data.DateTime.dt.date <= pd.to_datetime(end))
    data = data[time_mask]
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=data.DateTime, y=data[first_y],
            mode='lines+markers',
        ),
        secondary_y=False,
    )
    # print(y1log, type(y1log))

    fig.add_trace(
        go.Scatter(x=data.DateTime, y=data[second_y],
            mode='lines+markers',
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title={'text': "Time Series from Samoylov", 'x': 0.5, 'y': 0.85},
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        # plot_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(title_text="Time")

    if y1log==['on']:
        y1type='log'
        y1style={}
    else:
        y1type=None
        y1style={'opacity':0.5}

    if y2log==['on']:
        y2type='log'
        y2style={}
    else:
        y2type=None
        y2style={'opacity':0.5}

    fig.update_yaxes(title_text=first_y, color=muted_blue, secondary_y=False,
    type=y1type)
    fig.update_yaxes(title_text=second_y, color=brick_red, secondary_y=True,
    type=y2type)

    colors = [trace.line["color"] for trace in fig.data]
    print(colors)
    if first_y is None:
        raise PreventUpdate
    else:
        return fig, y1style, y2style, first_y, second_y, y1_info, y2_info

# Toggle information
@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# Scatter plot
@app.callback(
    [
        Output(component_id='scatter-plot', component_property='figure'),
        Output('text-output', 'children'),
        Output('x-log', 'style'),
        Output('y-log', 'style'),
        Output('color-log', 'style')
    ],
    [
        Input('x_selected', 'value'),
        Input('y_selected', 'value'),
        Input('color_selected', 'value'),
        Input('scatter-plot-date-range', 'start_date'),
        Input('scatter-plot-date-range', 'end_date'),
        Input('linear-fit', 'value'),
        Input('log-fit', 'value'),
        Input('power-fit', 'value'),
        Input('x-log', 'value'),
        Input('y-log', 'value'),
        Input('color-log', 'value')
    ]
)



def update_scatter_plot(x_selected, y_selected, color, start, end, lin_fit, log_fit, pow_fit, xlog, ylog, colorlog):

    # filtering data
    x_name = x_selected.split()[0]
    y_name = y_selected.split()[0]
    data = df.copy()
    time_mask = (data.DateTime.dt.date >= pd.to_datetime(start)) & (data.DateTime.dt.date <= pd.to_datetime(end))
    data = data[time_mask]

    x=data[x_selected]
    y=data[y_selected]
    nan_mask = ~np.isnan(x) & ~np.isnan(y)
    x = x[nan_mask]
    y = y[nan_mask]
    # x = x.iloc[np.argsort(x)]
    # y = y.iloc[np.argsort(x)]
    # print(x, y)
    # y = y[nan_mask][
    # x = x[nan_mask][np.argsort(x)]

    # log colorbar
    if colorlog == ['on']:
        cstyle={}
        tp='1e'
        c=np.log10(df[color][time_mask])
    else:
        cstyle={'opacity':0.5}
        tp=None
        c=df[color][time_mask]

    # draw plot
    scatter = px.scatter(data, x=data[x_selected], y=data[y_selected],
    color=c, color_continuous_scale='viridis'
    )
    scatter.update_traces(name='sample points', showlegend = True)

    # log x- and y-axis
    if xlog == ['on']:
        scatter.update_xaxes(type="log")
        xstyle={}
    else:
        xstyle={'opacity':0.5}
    if ylog == ['on']:
        scatter.update_yaxes(type="log")
        ystyle={}
    else:
        ystyle={'opacity':0.5}


    fitcards = []   # output children diplaying fit parameters


    # linear fit

    if lin_fit==['on']:

        # linfit = linregress(x[nan_mask], y[nan_mask])

        linfit = linregress(x, y)

        scatter.add_trace(go.Scatter(x=np.sort(x), y=linfit.slope*np.sort(x)+linfit.intercept, mode='lines', name='linear fit', line=dict(color=clinfit, dash='dash')))

        linfitcol = dbc.Col(
        dbc.Card(
            [
                dbc.CardHeader(html.H6('Linear Fit', style={'font-weight': 'bold', 'color':clinfit, 'text-align':'center'})),
                dbc.CardBody(
                    [
                        html.P('y = m \U000022C5 x + n', className='fit-text', style={'color': clinfit}),
                        html.P(f'm = {linfit.slope:.2f} ± {linfit.stderr:.2f}', className='fit-text'),
                        html.P(f'n = {linfit.intercept:.2f} ± {linfit.intercept_stderr:.2f}', className='fit-text'),
                        html.P(f'R\U000000B2 = {linfit.rvalue:.2f}', className='fit-text')
                    ]
                )
            ],
            color="primary",
            outline=True
        ),
        # width=4,
        xl=4, lg=4, md=8, sm=11, xs=11
        )

        fitcards.append(linfitcol)


    # logarithmic fit

    if log_fit == ['on']:


        # x = data[x_selected][nan_mask]
        # y=data[y_selected][nan_mask]
        def logfit(x, m, n):
            return m * np.log(x) + n
        # lpopt, lpcov = curve_fit(logfit, x[nan_mask], y[nan_mask])
        lpopt, lpcov = curve_fit(logfit, x, y)
        lperr = np.sqrt(np.diag(lpcov))
        res = y - logfit(x, *lpopt)
        sqsum_res = np.sum(res**2)
        sqsum_tot = np.sum((y-np.mean(y))**2)
        Rsq_log = 1 - sqsum_res/sqsum_tot
        # logfit = linregress(np.log(x[nan_mask]), y[nan_mask])

        # scatter.add_trace(go.Scatter(x=x, y=logfit.slope*x+logfit.intercept, mode='lines', name='log fit', line=dict(color='red', dash='dash')))

        if lperr[1] != np.inf:
            scatter.add_trace(go.Scatter(x=np.sort(x), y=logfit(np.sort(x), *lpopt), mode='lines', name='logarithmic fit',
                line=dict(color=clogfit, dash='dot')
                ))

            logfitcol = dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H6('Logarithmic Fit', style={'font-weight': 'bold', 'color':clogfit, 'text-align':'center'}),
                            # html.P('y = m \U000022C5 log (x) + n', style={'font-weight': 'bold', 'color':clogfit, 'text-align': 'center'}),
                            ),
                        dbc.CardBody(
                            [
                                html.P('y = m \U000022C5 log (x) + n', className='fit-text', style={'color': clogfit}),
                                html.P(f'm = {lpopt[0]:.2f} ± {lperr[0]:.2f}', className='fit-text'),
                                html.P(f'n = {lpopt[1]:.2f} ± {lperr[1]:.2f}', className='fit-text'),
                                html.P(f'R\U000000B2 = {Rsq_log:.2f}', className='fit-text')
                            ]
                        )
                    ],
                    color="success",
                    outline=True
                ),
                # width=4
                xl=4, lg=4, md=8, sm=11, xs=11
                )
            # except ValueError:
            #     logfitcol=[]
        else:
            logfitcol = dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H6('Logarithmic Fit', style={'font-weight': 'bold', 'color':clogfit, 'text-align':'center'}),
                            # html.P('y = m \U000022C5 log (x) + n', style={'font-weight': 'bold', 'color':clogfit, 'text-align': 'center'}),
                            ),
                        dbc.CardBody(
                            [
                                html.P('y = m \U000022C5 log (x) + n', className='fit-text', style={'color': clogfit}),
                                html.P('The calculation of a logarithmic fit is mathematically not possible for the selected parameters.',
                                    style={'text-align':'center'})
                                # html.P(f'm = {lpopt[0]:.2f} ± {lperr[0]:.2f}', className='fit-text'),
                                # html.P(f'n = {lpopt[1]:.2f} ± {lperr[1]:.2f}', className='fit-text'),
                                # html.P(f'R\U000000B2 = {Rsq_log:.2f}', className='fit-text')
                            ]
                        )
                    ],
                    color="success",
                    outline=True
                ),
                # width=4
                xl=4, lg=4, md=8, sm=11, xs=11
                )

        fitcards.append(logfitcol)


    # power fit

    if pow_fit == ['on']:

        x=data[x_selected]
        y=data[y_selected]
        def pow(x, a, b, c):
            return a * np.power(x, b) + c
        ppopt, ppcov = curve_fit(pow, x[nan_mask], y[nan_mask])
        # ppopt, ppcov = curve_fit(pow, x, y)
        pperr = np.sqrt(np.diag(ppcov))
        res = y - pow(x, *ppopt)
        sqsum_res = np.sum(res**2)
        sqsum_tot = np.sum((y-np.mean(y))**2)
        Rsq_pow = 1 - sqsum_res/sqsum_tot

        if pperr[1] != np.inf:
            scatter.add_trace(go.Scatter(x=np.sort(x), y=pow(np.sort(x), *ppopt), mode='lines', name='power fit', line=dict(color=cpowfit, dash='dashdot')))

            powfitcol = dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H6('Power Fit', style={'font-weight': 'bold', 'color':cpowfit, 'text-align':'center'})),
                        dbc.CardBody(
                            [
                                html.P('y = a \U000022C5 x\U00001D47 + c', className='fit-text', style={'color': cpowfit}),
                                html.P(f'a = {ppopt[0]:.2e} ± {pperr[0]:.2e}', className='fit-text'),
                                html.P(f'b = {ppopt[1]:.2f} ± {pperr[1]:.2f}', className='fit-text'),
                                html.P(f'c = {ppopt[2]:.2f} ± {pperr[2]:.2f}', className='fit-text'),
                                html.P(f'R\U000000B2 = {Rsq_pow:.2f}', className='fit-text')
                            ]
                        )
                    ],
                    color="danger",
                    outline=True
                ),
                # width=4
                xl=4, lg=4, md=8, sm=11, xs=11
                )
        else:
            powfitcol = dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H6('Power Fit', style={'font-weight': 'bold', 'color':cpowfit, 'text-align':'center'})),
                        dbc.CardBody(
                            [
                                html.P('y = a \U000022C5 x\U00001D47 + c', className='fit-text', style={'color': cpowfit}),
                                html.P('The calculation of a power fit is mathematically not possible for the selected parameters.',
                                    style={'text-align':'center'})
                                # html.P(f'a = {ppopt[0]:.2e} ± {pperr[0]:.2e}', className='fit-text'),
                                # html.P(f'b = {ppopt[1]:.2f} ± {pperr[1]:.2f}', className='fit-text'),
                                # html.P(f'c = {ppopt[2]:.2f} ± {pperr[2]:.2f}', className='fit-text'),
                                # html.P(f'R\U000000B2 = {Rsq_pow:.2f}', className='fit-text')
                            ]
                        )
                    ],
                    color="danger",
                    outline=True
                ),
                # width=4
                xl=4, lg=4, md=8, sm=11, xs=11
                )
        # print(ppopt[0])
        fitcards.append(powfitcol)


    scatter.update_layout(
        coloraxis_colorbar={'title':color, 'tickprefix':tp, 'titleside':'right'},
        title={'text': f"{y_name} vs. {x_name}", 'x': 0.5, 'y': 0.93},
        legend={'x':0.02, 'y':0.98, 'xanchor':'left', 'yanchor':'top'}
    )


    return scatter, fitcards, xstyle, ystyle, cstyle


# Slideshow

@app.callback(
    [
        Output("img-description", 'children'),
        Output("img-slide", 'src'),
        # Output('image-counter', 'children')
    ],
    [
        Input('btn_prev', 'n_clicks'),
        Input('btn_next', 'n_clicks')
    ],
    prevent_initial_call=True
)

def slide(prev_clicks, next_clicks):

    image_list = [
        'assets/slideshow1.png',
        'assets/slideshow2.png',
        'assets/map_example.png'
    ]

    image_descriptions = [
        'This example image shows a part of the Lena Delta in bright colors.',
        'This example image shows the whole Lena Delta in bright colors.',
        'This example image is a screenshot from Google Maps. It would be more convenient if all images had the same height though.'
    ]



    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if prev_clicks != None and next_clicks!= None:
        if next_clicks >= len(image_list):
            next_clicks %= len(image_list)
        if prev_clicks >= len(image_list):
            prev_clicks %= len(image_list)

        n = next_clicks - prev_clicks

    elif next_clicks!= None:
        if next_clicks >= len(image_list):
            next_clicks %= len(image_list)
        # if prev_clicks < -len(image_list):
        #     prev_clicks %= len(image_list)
        n =  next_clicks

    elif prev_clicks!= None:
        if prev_clicks >= len(image_list):
            prev_clicks %= len(image_list)
        n = -prev_clicks

    return image_descriptions[n], image_list[n]#, f'{n}/{len(image_list)}'
# Download data
# filtered csv
@app.callback(
    Output("download-dataframe-csv", "data"),
    [
        Input("btn_csv", "n_clicks"),
        Input('download-parameter', 'value'),
        Input('download-date-range', 'start_date'),
        Input('download-date-range', 'end_date')
    ],
    prevent_initial_call=True,
)
def func(n_clicks, columns, start, end):
    data = df.copy()
    time_mask = (data.DateTime.dt.date >= pd.to_datetime(start)) & (data.DateTime.dt.date <= pd.to_datetime(end))
    selected_data = data[time_mask][columns]
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn_csv.n_clicks' in changed_id:
        return dcc.send_data_frame(selected_data.to_csv, "LenaMonitoringData_filtered.csv")

# full csv
@app.callback(
    Output("download-dataframe-csv_full", "data"),
    Input("btn_csv_full", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df.to_csv, "LenaMonitoringData_full.csv")

# filtered excel
@app.callback(
    Output("download-dataframe-xlxs", "data"),
    [
        Input("btn_xlxs", "n_clicks"),
        Input('download-parameter', 'value'),
        Input('download-date-range', 'start_date'),
        Input('download-date-range', 'end_date')
    ],
    prevent_initial_call=True,
)
def func(n_clicks,columns, start, end):
    data = df.copy()
    time_mask = (data.DateTime.dt.date >= pd.to_datetime(start)) & (data.DateTime.dt.date <= pd.to_datetime(end))
    selected_data = data[time_mask][columns]
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn_xlxs.n_clicks' in changed_id:
        return dcc.send_data_frame(selected_data.to_excel, "LenaMonitoringData_filtered.xlxs", sheet_name="Sheet_1")

# full excel
@app.callback(
    Output("download-dataframe-xlxs_full", "data"),
    Input("btn_xlxs_full", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df.to_excel, "LenaMonitoringData_full.xlxs", sheet_name="Sheet_1")


if __name__ == '__main__':
    app.run_server(debug=True)
