from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os




# import data
df = pd.read_csv('data/DUCCEM_sampling_list.csv', parse_dates=['Date'], na_values='n.a.', sep=";")
df['Day of Year'] = df.Date.dt.dayofyear
df['Year'] = df.Date.dt.year
df['Month'] = df.Date.dt.month


# import discharge data and add to df
dis = pd.read_csv('data/Mackenzie_ArcticRedRiver_Version_20230809.csv',
    parse_dates=['date'], index_col='date', sep=";"
)

df['Discharge'] = dis.loc[list(df.Date)].discharge.values
#print(list(df.Date))
#print(dis.iloc['date'])


# import parameter information
info = pd.read_csv('data/Parameter_Info_Mackenzie.csv', sep=";")
#print(df.columns.values)
#print(info.Name.values)

ts_mask = info['For Timeseries']=='Yes'
sc_mask = info['For Scatter']=='Yes'
new_label_mask = info['Renamed (unit)'].isnull()==False

ts_alphabetic = np.argsort([str.casefold(i) for i in info.Name[ts_mask]])
sc_alphabetic = np.argsort([str.casefold(i) for i in info.Name[sc_mask]])
dl_alphabetic = np.argsort([str.casefold(i) for i in info.Name])

labels = info.Name.copy()
labels[new_label_mask] = info['Renamed (unit)'][new_label_mask]

# check if files match
if sum(df.columns.values != info.Name.values) > 0:
    raise ValueError('The columns of the data file and the Names in the info file do not match!')

# set values below QF to np.nan
#ii = range(45,79,2) # ion indices, modify when ions are added
#for i, col in zip(ii, df.columns[ii]):
#    df.loc[df.iloc[:, i] < df.iloc[:, i+1], col] = np.nan



# define columns to use
not_used = set()
remove_str = ['ID', 'QF', 'cations and anions', 'cuvette lenght', 'Instrument']
for c in df.columns:
    for r in remove_str:
        if r in c:
            not_used.add(c)
used_cols = sorted([col for col in df.columns if col not in not_used], key=str.casefold)


#info = pd.read_csv('data/Parameter_Info_Mackenzie.csv')

# images for slideshow
image_list = os.listdir('assets/Pictures/compressed')
image_descriptions = [str.split(i, 'png')[0] for i in image_list]
rights = [str.split(i, '. ')[-1] for i in image_descriptions]

# define colors
#clinfit = 'royalblue'
clinfit = 'royalblue'
clogfit = 'green'
cpowfit = 'firebrick'
theme = '#3d837f' #'#3d837f'
theme_second = '#dbe7f5'
muted_blue = 'royalblue'
brick_red = 'crimson'
darklink = '#373a3c'

# navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Time Series", href="/#time-series", external_link=True)),
        dbc.NavItem(dbc.NavLink("Correlations", href="/#correlations", external_link=True)),
        dbc.NavItem(dbc.NavLink("Impressions", href="/#impressions", external_link=True)),
        #dbc.NavItem(dbc.NavLink("Download", href="/#download", external_link=True)),
        #dbc.NavItem(dbc.NavLink("The Station", href="/#the-station", external_link=True)),
        dbc.NavItem(dbc.NavLink("Related Info", href="/#related-info", external_link=True)),
        dbc.NavItem(dbc.NavLink("Team", href="/team", external_link=True)), #target='_blank' ->add if you want to open a new tab
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Email", header=True),
                dbc.DropdownMenuItem(html.A("\U00002709 bennet.juhls@awi.de", href="mailto:bennet.juhls@awi.de", style={'color':darklink}),)
            ],
            nav=True,
            in_navbar=True,
            label="Contact",
        ),
        # dbc.NavItem(dbc.NavLink("\U00002302 Home", href="/", external_link=True)),
    ],
    # brand="Home",
    brand_href="/",
    brand_style={'font-size':'11pt', 'color': 'grey'},
    color=theme,
    dark=True,
    sticky='top',
    expand='lg'
    # fixed='top'
)

header = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.A(
                html.Img(src='assets/Logo_MackenzieRiverSampling.png', width='100%', title='Home'),
                href='/',
                className='header-image'
            ),
            width=5,
            xl=3, lg=3, md=3, sm=2, xs=2
        ),
        dbc.Col(
            [
                html.H1(
                    [
                        "Explore the biogeochemistry of the Mackenzie River (East Channel, Inuvik)",
                        html.Br(),
                    ],
                     className='header-title',
                     style={'font-size': '18px'}
                ),
                html.P(
                    #children=[
                    ['The research leading to these results has received funding from the European ',
                      'Union’s Horizon 2020 project Interact under grant agreement No 730938, click for more info about ', 
                      html.A( ' INTERACT', href='https://eu-interact.org/', target='_blank', 
                      style={"color": "black"}
                      )
                    ],
                        
                        #' The research leading to these results has received funding from the European',
                        #' Union’s Horizon 2020 project Interact under grant agreement No 730938.',
                        #href='https://www.awi.de/en/about-us/organisation/staff/sofia-antonova.html'
                        
                    #],
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

    ],
    className='header',
),

# footer
footer = dbc.Container(
    [
        dbc.Row([
            dbc.Col(
                html.A(
                    html.Img(
                        className='footer-image',
                        src='assets/1200px-AWI_Logo_2017.svg.png',
                        # style={'height': '50px'},
                        title='Alfred Wegener Institute (AWI)'),
                    href='https://www.awi.de/en/',
                    target="_blank"
                    ),
                # width=1
            ),
            dbc.Col(
                html.P([
                    html.A('Imprint', href="/imprint",
                        style={"color": "#28b4e6", 'font-size': '17px'}
                        )
                        ])
                    # width=2
                    ),
            dbc.Col(
                html.P([
                    html.A('Accessibility', href="/accessibility",
                        style={"color": "#28b4e6", 'font-size': '17px'}
                        )
                        ])
                    # width=2
                    ),
            dbc.Col(
                html.P([
                    html.A('Privacy Notice', href= 'https://www.awi.de/en/privacy-protection.html' , target='_blank',
                            style={"color": "#28b4e6", 'font-size': '17px'}
                            )
                            ]),
                        # width=2
                    ),
            
                ],
        justify='center',
        align='center',
                ),

    ],
    className='footer'
)





# layout of the main page
main_page = dbc.Container([
    navbar,
    header[0], # why 0? why list of lists?
    # login_form,
    html.Div(id='custom-auth-frame'),
    html.Div(id='custom-auth-frame-1',
               style={
                      'textAlign': 'right',
                      "background": "black",
               }
               ),
    # time series plot
    dbc.Card(id='time-series', children=[
        dbc.CardHeader(html.H4('Explore the Time Series'), id='explore'),
        dbc.CardBody([
            dbc.Row([
            dbc.Col(
                [
                    dbc.Row([
                    dbc.Col(html.P('Select first y-value', className='menu-title'),
                        # width=8,
                        xl=8, lg=8, md=8, sm=8, xs=8,
                    ),
                    dbc.Col(dcc.Checklist(
                        id='y1-log',
                        options=[{'label': ' log scale', 'value': 'on'}],
                        value=[],
                        # style={'margin-bottom':'-12px'},
                        className='menu-title'
                    ))
                    ], align='bottom', justify='between'),
                    dcc.Dropdown(
                        id='first_y',
                        # options=[
                        #     {'label': l, 'value': l} for l in used_cols
                        # ],
                        options=[
                            {'label': labels[ts_mask].values[ts_alphabetic][i], 'value': colname} for i, colname in enumerate(df.columns[ts_mask][ts_alphabetic])
                        ],
                        multi=False,
                        style={'width': '100%'},
                        value='Discharge',
                        className='dropdown',
                    ),
                    dbc.Row([
                    dbc.Col(html.P('Select second y-value', className='menu-title'),
                        # width=8,
                        xl=8, lg=8, md=8, sm=8, xs=8,
                    ),
                    dbc.Col(dcc.Checklist(
                        id='y2-log',
                        options=[{'label': ' log scale', 'value': 'on'}],
                        value=[],
                        className='menu-title'
                    ))
                    ], align='bottom', justify='between'),
                    dcc.Dropdown(
                        id='second_y',
                        # options=[
                        #     # {'label': l, 'value': l} for l in sorted(df.columns[6:], key=str.casefold)
                        #     {'label': l, 'value': l} for l in used_cols
                        # ],
                        options=[
                            {'label': labels[ts_mask].values[ts_alphabetic][i], 'value': colname} for i, colname in enumerate(df.columns[ts_mask][ts_alphabetic])
                        ],
                        multi=False,
                        style={'width': '100%'},
                        value='EC (µS/cm)',
                        className='dropdown',
                    ),
                    html.P('Select Time Window', className='menu-title'),
                    dcc.DatePickerRange(
                        id='time-series-date-range',
                        min_date_allowed=df.Date.min().date(),
                        max_date_allowed=df.Date.max().date(),
                        start_date=df.Date.min().date(),
                        end_date=df.Date.max().date(),
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
                xl=4, lg=4, md=6, sm=8, xs=10,
                align='center'
                ),
            # dbc.Col()
            dbc.Col(
                [
                    dcc.Graph(
                        id='time-series-plot',
                        config={
                            'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian'],
                            'displaylogo': False,
                            'toImageButtonOptions': {
                                'format': 'svg', # one of png, svg, jpeg, webp
                                'filename': 'Mackenzie_time_series',
                            }
                        }
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
                            className='param-card',
                            children=dbc.CardBody([
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
                            className='param-card',
                            children=dbc.CardBody([
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
                    'margin-bottom':'0px',
                    'margin-top':'-12px',
                    }
            ),
            id="collapse",
            is_open=False,
        ),
        ]),
    ]),


    # scatter plot
    dbc.Card(id='correlations', children=[
        dbc.CardHeader(html.H4('Parameter correlations')),
        dbc.CardBody([dbc.Row([
            dbc.Col(
                [
                    html.Div(style={'margin-bottom':'24px'}),
                    dbc.Row([
                    dbc.Col(html.P('Select x-value', className='menu-title'),
                        width=8,
                        xl=8, lg=8, md=8, sm=8, xs=8,
                    ),
                    dbc.Col(dcc.Checklist(
                        id='x-log',
                        options=[{'label': ' log scale', 'value': 'on'}],
                        value=[],
                        className='menu-title'
                    ))
                    ], align='bottom', justify='between'),
                    dcc.Dropdown(
                        id='x_selected',
                        # options=[
                        #     {'label': l, 'value': l} for l in used_cols
                        # ],
                        options=[
                            {'label': labels[sc_mask].values[sc_alphabetic][i], 'value': colname} for i, colname in enumerate(df.columns[sc_mask][sc_alphabetic])
                        ],
                        multi=False,
                        style={'width': '100%'},
                        value='Temperature (°C)',
                        # value = 'Temperature (°C)',
                        # value = 'Conductivity lab (µS/cm)',
                        className='dropdown',

                        ),
                    dbc.Row([
                    dbc.Col(html.P('Select y-value', className='menu-title'),
                        width=8,
                        xl=8, lg=8, md=8, sm=8, xs=8,
                    ),
                    dbc.Col(dcc.Checklist(
                        id='y-log',
                        options=[{'label': ' log scale', 'value': 'on'}],
                        value=[],
                        className='menu-title'
                    ))
                    ], align='bottom', justify='between'),
                    dcc.Dropdown(
                        id='y_selected',
                        # options=[
                        #     {'label': l, 'value': l} for l in used_cols
                        # ],
                        options=[
                            {'label': labels[sc_mask].values[sc_alphabetic][i], 'value': colname} for i, colname in enumerate(df.columns[sc_mask][sc_alphabetic])
                        ],
                        multi=False,
                        style={'width': '100%'},
                        value='EC (µS/cm)',
                        # value = 'Temperature (°C)',
                        # value = 'logy_artificial',
                        # value = 'Conductivity in situ (µS/cm)',
                        className='dropdown',
                    ),
                    dbc.Row([
                    dbc.Col(html.P('Select color', className='menu-title'),
                        width=8,
                        xl=8, lg=8, md=8, sm=8, xs=8,
                    ),
                    dbc.Col(dcc.Checklist(
                        id='color-log',
                        options=[{'label': ' log scale', 'value': 'on'}],
                        value=[],
                        className='menu-title'
                    ))
                    ], align='bottom', justify='between'), #, no_gutters=True
                    dcc.Dropdown(
                        id='color_selected',
                        # options=[
                        #     # {'label': l, 'value': l} for l in sorted(df.columns[6:], key=str.casefold)
                        #     {'label': l, 'value': l} for l in used_cols
                        # ],
                        options=[
                            {'label': labels[sc_mask].values[sc_alphabetic][i], 'value': colname} for i, colname in enumerate(df.columns[sc_mask][sc_alphabetic])
                        ],
                        multi=False,
                        style={'width': '100%'},
                        # value='Day of Year',
                        value = 'Discharge',
                        className='dropdown',
                    ),
                    html.P('Select Time Window', className='menu-title'),
                    dcc.DatePickerRange(
                        id='scatter-plot-date-range',
                        min_date_allowed=df.Date.min().date(),
                        max_date_allowed=df.Date.max().date(),
                        start_date=df.Date.min().date(),
                        end_date=df.Date.max().date(),
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
                xl=4, lg=4, md=6, sm=8, xs=10,
                align='start',
                # style={'margin-bottom': '24px'},
                ),


            dbc.Col(
                [
                    dcc.Graph(
                        id='scatter-plot',
                        config={
                            'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian'],
                            'displaylogo': False,
                            'toImageButtonOptions': {
                                'format': 'svg', # one of png, svg, jpeg, webp
                                'filename': 'Mackenzie_scatter_plot',
                            }
                        },
                        style={'margin-bottom': '-20px'}
                    ),
                    dbc.Row([
                        dbc.Col(
                            dbc.Collapse(
                                html.Div(id='linfit-card'),
                                id='linfit-collapse',
                                is_open=False
                            ),
                            xl=4, lg=4, md=8, sm=11, xs=11,
                        ),
                        dbc.Col(
                            dbc.Collapse(
                                html.Div(id='logfit-card'),
                                id='logfit-collapse',
                                is_open=False
                            ),
                            xl=4, lg=4, md=8, sm=11, xs=11,
                        ),
                        dbc.Col(
                            dbc.Collapse(
                                html.Div(id='powfit-card'),
                                id='powfit-collapse',
                                is_open=False
                            ),
                            xl=4, lg=4, md=8, sm=11, xs=11,
                        ),
                    ],
                    justify='center'
                    )
                ],
                # width=8
                xl=8, lg=8, md=10, sm=12, xs=12,
            )
            ],
            justify='around',
        ),
        ]),
    ]),

    # Slideshow
    dbc.Card(id='impressions',
        children=[
            dbc.CardHeader(html.H4('Impressions')),
            # dbc.CardImg(id='img-slide', src="assets/slideshow1.png", top=True, className='center-block, slideshow-image'),
            dbc.CardBody([
                dbc.Row(
                    # dbc.Col(
                        html.Img(id='img-slide', src=f"assets/Pictures/compressed/{image_list[0]}", className='slideshow-image', title=rights[0]), # center-block'), #, slideshow-image'),
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
                                html.P(image_descriptions[0],
                                    id='img-description',
                                    className='img-text',
                                    style={'text-align': 'center'}
                                ),
                            justify='center',
                            align='center',
                            style={'height':'48px'}
                            ),
                            # html.P(id='image-counter')
                        ],
                        xl=8, lg=8, md=8, sm=8, xs=6),
                    dbc.Col(
                        dbc.Row(html.Button("\U0000276F", id="btn_next", className="btn btn-primary, button"), justify='end'),
                        xl=1, lg=1, md=1, sm=2, xs=3),
                ],
                justify='around',
                align='center',
                # style={'margin-bottom':'-24px'}
                )
            ])
        ]
    ),





    # Download section
     # 

    # The Station
    # dbc.Card(id='the-station',
        # children=[
            # dbc.CardHeader(html.H4('The Samoylov Island Research Station')),
            # dbc.CardBody([
                # dcc.Link(
                    # [
                        # dbc.CardImg(src='assets/Samoylov_station_summer.jpg',
                            # top=True,
                            # className='center-block',
                            # title='Click to learn more about the Samoylov Island Research Station'
                        # ),
                        # html.P('About the station and island',
                            # className='text',
                            # style={'text-align':'center', 'margin-top':'12px'}) # 'color': darklink,
                    # ],
                    # href='https://www.awi.de/en/expedition/stations/island-samoylov.html',
                    # target='_blank',
                    # )
            # ])
        # ]

    # ),

    # Read more
    dbc.Card(id='related-info', children=[
        dbc.CardHeader(html.H4('Related Info')),
        dbc.CardBody(
            children=[
                dbc.Row([
                    dbc.Col(
                        [
                            # Arctic Gro
                            dcc.Link(
                            dbc.Card(
                                className='internal-card',
                                children=[
                                dbc.CardImg(src="assets/ArcticGreatRiversObservatory.png", top=True, className='preview-image'),
                                dbc.CardBody([
                                    html.P(
                                        "Visit the Arctic Great Rivers Observatory Webpage",
                                        className="text",
                                        )
                                ]),
                            ],
                            ),
                            href='https://arcticgreatrivers.org/',
                            target="_blank",
                            style={'color':darklink}
                            ),
                            html.Div(style={'margin-top': '20px'}),
                            #
                        ],
                    xl=6, lg=6, md=10, sm=12, xs=12
                    ), # end of col
                    
                    dbc.Col(
                        [
                            # ARI
                            dcc.Link(
                            dbc.Card(
                                className='internal-card',
                                children=[
                                dbc.CardImg(src="assets/ARI_logo.png", top=True, className='preview-image'),
                                dbc.CardBody([
                                    html.P(
                                        "Visit the webpage of our Partner for the water sampling in Inuvik",
                                        className="text",
                                        )
                                ]),
                            ],
                            ),
                            href='https://nwtresearch.com/about/regional-research-centres/western-arctic-research-centre',
                            target="_blank",
                            style={'color':darklink}
                            ),
                            html.Div(style={'margin-top': '20px'}),
                            #
                        ],
                    xl=6, lg=6, md=10, sm=12, xs=12
                    ), # end of col
                    
                    dbc.Col(
                        [
                            # Interact
                            dcc.Link(
                            dbc.Card(
                                className='internal-card',
                                children=[
                                dbc.CardImg(src="assets/Interact_logo.png", top=True, className='preview-image'),
                                dbc.CardBody([
                                    html.P(
                                        "This project received fundings by INTERACT",
                                        className="text",
                                        )
                                ]),
                            ],
                            ),
                            href='https://eu-interact.org/',
                            target="_blank",
                            style={'color':darklink}
                            ),
                            html.Div(style={'margin-top': '20px'}),
                            #
                        ],
                    xl=6, lg=6, md=10, sm=12, xs=12
                    ), # end of col
                    
                                

                ],
                justify='around'
                ) # end of row
            ]
        ) # end of card body
    ]),


    # footer
    footer



])



# layout of the team page

team_page = dbc.Container([
    navbar,
    header[0],

    dbc.Card(id='the-team',
        children=[
            dbc.CardHeader(html.H4('The Team')),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(
                        dbc.Card([
                            dbc.CardImg(src='assets/PhotoBennet_ship.png'),
                            dbc.CardBody([
                                html.H5('Bennet Juhls'), # pay attention to name legth
                                html.H6('Postdoctoral researcher'),
                                html.P('Alfred Wegener Institute, Helmholtz Centre for Polar and Marine Research (AWI)'),
                                html.A('Personal institute page', href='https://www.awi.de/en/about-us/organisation/staff/bennet-juhls.html', target='_blank')
                            ],
                            className='team-card'
                            )

                        ]),
                        xl=3, lg=3, md=4, sm=6, xs=12
                    ),
                    dbc.Col(
                        dbc.Card([
                            dbc.CardImg(src='assets/Erika.png'),
                            dbc.CardBody([
                                 html.H5('Erika Hille'), # pay attention to name legth
                                 html.H6('Special Projects Coordinator/Librarian'),
                                 html.P('Western Arctic Research Centre (WARC), Aurora Research Institute (ARI)'),
                                 html.A('Personal institute page', href='https://nwtresearch.com/about-us/people/erika-hille', target='_blank')
                            ],
                            className='team-card'
                            )

                        ]),
                        xl=3, lg=3, md=4, sm=6, xs=12
                    ),
                    dbc.Col(
                        dbc.Card([
                            dbc.CardImg(src='assets/morgenstern.JPG'),
                            dbc.CardBody([
                                html.H5('Anne Morgenstern'), # pay attention to name legth
                                html.H6('Senior scientist'),
                                html.P('Alfred Wegener Institute, Helmholtz Centre for Polar and Marine Research (AWI)'),
                                html.A('Personal institute page', href=' https://www.awi.de/ueber-uns/organisation/mitarbeiter/anne-morgenstern.html', target='_blank')
                            ],
                            className='team-card'
                            )

                        ]),
                        xl=3, lg=3, md=4, sm=6, xs=12
                    ),
                    dbc.Col(
                        dbc.Card([
                            dbc.CardImg(src='assets/Overduin_sweden.jpg'),
                            dbc.CardBody([
                                html.H5('Paul Overduin'), # pay attention to name legth
                                html.H6('Senior scientist'),
                                html.P('Alfred Wegener Institute, Helmholtz Centre for Polar and Marine Research (AWI)'),
                                html.A('Personal institute page', href='https://www.awi.de/en/about-us/organisation/staff/paul-overduin.html', target='_blank')
                            ],
                            className='team-card'
                            )

                        ]),
                        xl=3, lg=3, md=4, sm=6, xs=12
                    ),
                    ],
                    justify='center',
                ),
                dbc.Row([
                     dbc.Col(
                         dbc.Card([
                             dbc.CardImg(src='assets/Lance_clip.png'),
                             dbc.CardBody([
                                 html.H5('Lance Gray'), # pay attention to name legth
                                 html.H6('Research & Outreach Assistant'),
                                 html.P('Western Arctic Research Centre (WARC), Aurora Research Institute (ARI)'),
                                 html.A('Personal institute page', href='https://www.auroracollege.nt.ca/staff-directory/lance-gray/', target='_blank')
                             ],
                             className='team-card'
                             )

                         ]),
                         xl=3, lg=3, md=4, sm=6, xs=12
                     ),
                    dbc.Col(
                        dbc.Card([
                            dbc.CardImg(src='assets/eulenbur_square.jpg'),
                            dbc.CardBody([
                                html.H5('Antje Eulenburg'), # pay attention to name legth
                                html.H6('Technical lab assistant'),
                                html.P('Alfred Wegener Institute, Helmholtz Centre for Polar and Marine Research (AWI)'),
                                html.A('Personal institute page', href='https://www.awi.de/ueber-uns/organisation/mitarbeiter/antje-eulenburg.html', target='_blank')
                            ],
                            className='team-card'
                            )

                        ]),
                        xl=3, lg=3, md=4, sm=6, xs=12
                    ),
                     dbc.Col(
                         dbc.Card([
                             dbc.CardImg(src='assets/Felica_clip.png'),
                             dbc.CardBody([
                                 html.H5('Felica Gehde'), # pay attention to name legth
                                 html.H6('Student assistant'),
                                 html.P('Alfred Wegener Institute, Helmholtz Centre for Polar and Marine Research (AWI)'),
                                 #html.A('Personal institute page', href='https://www.awi.de/en/about-us/organisation/staff/sofia-antonova.html', target='_blank')
                             ],
                             className='team-card'
                             )

                         ]),
                         xl=3, lg=3, md=4, sm=6, xs=12
                     ),
                     dbc.Col(
                         dbc.Card([
                             dbc.CardImg(src='assets/Lisa.png'),
                             dbc.CardBody([
                                 html.H5('Lisa Broeder'), # pay attention to name legth
                                 html.H6('Postdoctoral Researcher'),
                                 html.P('ETH Zürich'),
                                html.A('Personal institute page', href='https://erdw.ethz.ch/personen/profil.MjQ0Nzg2.TGlzdC83NzMsOTI0MjA1OTI2.html', target='_blank')
                             ],
                             className='team-card'
                             )

                         ]),
                         xl=3, lg=3, md=4, sm=6, xs=12
                     ),
                     ],
                    justify='center',
                ),
                dbc.Row([
                     dbc.Col(
                         dbc.Card([
                             dbc.CardImg(src='assets/Foto SRokitta and Nicolas the Seal.jpg'),
                             dbc.CardBody([
                                 html.H5('Sebastian Rokitta'), # pay attention to name legth
                                 html.H6('Senior scientist'),
                                 html.P('Alfred Wegener Institute, Helmholtz Centre for Polar and Marine Research (AWI)'),
                                html.A('Personal institute page', href='https://www.awi.de/ueber-uns/organisation/mitarbeiter/detailseite/sebastian-rokitta.html', target='_blank')
                             ],
                             className='team-card'
                             )

                         ]),
                         xl=3, lg=3, md=4, sm=6, xs=12
                     ),
                     dbc.Col(
                         dbc.Card([
                             dbc.CardImg(src='assets/Julie.png'),
                             dbc.CardBody([
                                 html.H5('Julie Lattaud'), # pay attention to name legth
                                 html.H6('Ambizione Fellow'), 
                                 html.P('Department of Environmental Sciences, University of Basel'),
                                 html.A('Personal page', href='https://julielattaud.mystrikingly.com/', target='_blank')
                             ],
                             className='team-card'
                             )

                         ]),
                         xl=3, lg=3, md=4, sm=6, xs=12
                     ),
                ],
                justify='center'),
                
            ])
        ]
    ),

    footer

])



# layout of the imprint page


imprint_page = dbc.Container([
    navbar,
    header[0],

    dbc.Card(children=[
        dbc.CardHeader(html.H4('Imprint')),
        dbc.CardBody(children=[
                        html.B(['Address'],
                        style={'font-size': '18px',"width": "100%","opacity": "unset"}
                                ),
                        html.P(['Alfred-Wegener-Institut', html.Br(),'Helmholtz Centre for Polar and Marine Research', html.Br(),' Am Handelshafen 12', html.Br(),'27570 Bremerhaven', html.Br(), 'Germany', html.Br(), html.Br(),'Tel.: +49 (0)471 4831-0', html.Br(),'Fax: +49 (0)471 4831-1149', html.Br(),'E-Mail: info@awi.de', html.Br(), html.A('www.awi.de', href= 'https://www.awi.de/en/' ,target='_blank',style={"color": "black"})
                        ]),
                        html.B(['Legal form'], style={'font-size': '18px',"width": "100%","opacity": "unset"}),
                        html.P(['The Alfred Wegener Institute is a foundation under public law. (Stiftung des öffentlichen Rechts) The AWI is a member of the Helmholtz Association of German Research Centres.']),
                        
                        html.B(['Representatives'], style={'font-size': '18px',"width": "100%","opacity": "unset"}),
                        html.P(['The Alfred Wegener Institute is legally represented by its Directorate:', html.Br(),'Prof. Dr. Antje Boetius (Director)', html.Br(),'Dr. Karsten Wurr (Administrative Director)', html.Br(), html.B('VAT'), ' identification number according to § 27a Umsatzsteuergesetz: DE 114707273']),
                        
                        html.B(['Editorial responsibility'], style={'font-size': '18px',"width": "100%","opacity": "unset"}),
                        html.P(['Bennet Juhls (bennet.juhls@awi.de)']),
                        
                        html.B(['Copyright'], style={'font-size': '18px',"width": "100%","opacity": "unset"}),
                        html.P(['The content of all web pages of this website is protected by copyright. All illustrations and images on the websites of the Alfred Wegener Institute may not be copied, reproduced or distributed without the permission of the AWI. A change of the meta data (IPTC data incl. naming of originator, source, copyright notice and terms of use) of the images is not permitted.']),
                        
                        html.B(['Rights of use'], style={'font-size': '18px',"width": "100%","opacity": "unset"}),
                        html.P(['The Alfred Wegener Institute authorises the following ',html.B('private use'),' of images on this website:', html.Br(), '- copying the images to your private computer', html.Br(), '- the printing of images for private archiving or decoration purposes', html.Br(), '- the forwarding of the images to friends and family, together with reference to their origin, mention of the copyright notice and reference to the purely private use requirement.',html.Br(),html.Br(),'The Alfred Wegener Institute authorises the following free use of images in the press section of this website for editorial journalistic publications under the following conditions:',html.Br(),'- The images used illustrate contributions about the work of the Alfred Wegener Institute.',html.Br(),'- The complete copyright notice is named as deposited in the metadata (IPTC data), i.e. in the form "Alfred-Wegener-Institute/Surname, first name"',html.Br(),'- the short form "AWI/Surname " may only be used if the full name of the institute is mentioned together with the abbreviation in the article.',html.Br(),html.Br(),'Images under a Creative Commons license may be used according to the license used.',html.Br(),html.Br(),'In general, the Alfred Wegener Institute',html.B(' does not '),'grant permission to use images on this website for the following purposes:',html.Br(),'- Advertising, design of advertisements, commercials etc.',html.Br(),'- Sale of products in which the focus is on images (T-shirts, coffee cups, large prints)',html.Br(),'- Sale of digital copies of image data.']),
                        
                        html.B(['Liability notice'], style={'font-size': '18px',"width": "100%","opacity": "unset"}),
                        html.P(['No liability is assumed for completeness, editorial and technical errors, topicality, omissions, etc. or the accuracy of the content, unless the author can be proven to have acted with intent or gross negligence.'])         
                    ])
                ]),
  
    footer

])



# layout of the Accessibility page


accessibility_page = dbc.Container([
    navbar,
    header[0],

    dbc.Card(children=[
        dbc.CardHeader(html.H4('Accessibility')),
        dbc.CardBody(children=[
        
        
                        html.B(['Compliance status'], style={'font-size': '18px',"width": "100%","opacity": "unset"}),
                        html.P(['This website is partially compliantiv with BITV 2.0, due to the non-compliances and/or the exemptions listed below.']),

                        html.B(['Non-accessible content'], style={'font-size': '18px',"width": "100%","opacity": "unset"}),
                        html.P(['The content listed below is non-accessible for the following reason(s):', html.Br(), 'non-compliance with the BITV 2.0']),

                        html.H6(['1. Color contrast'], style={'font-size': '16px',"width": "100%","opacity": "unset"}),
                        html.P(['Description: Contrast between text color and background color is insufficient for some elements.', html.Br(), 'Measure: Introduction of a button to see a high-contrast color variant.']),

                        html.H6(['2. Missing alternative texts'], style={'font-size': '16px',"width": "100%","opacity": "unset"}),
                        html.P(['Description: Many visual elements lack a corresponding alternative text.']),
                                        
                        html.B(['Feedback and contact information:'],
                        style={'font-size': '18px',"width": "100%","opacity": "unset"}
                                ),
                        html.P(['We would like to further improve our offer. Feel free to share your digital accessibility issues and questions with us: barrierefreiheit@awi.de'
                        ]),

                        
                    ])
                ]),
  
    footer

])


