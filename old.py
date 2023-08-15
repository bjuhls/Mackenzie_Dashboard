import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import seaborn as sns
import pandas as pd
from datetime import datetime
import dash
import plotly

today = datetime.now().timetuple().tm_yday

# import data
df = pd.read_excel('data/Lena_Kyusyur_1936_2020_corrected.xlsx', index_col='Datetime Samoylov')
years = df.index.year.unique()
grouped = df.groupby(df.index.year).mean()
grouped.index = pd.to_datetime(grouped.index, format='%Y')
tc = pd.read_excel('data/Overview.xlsx', parse_dates={'datetime': ['Date', 'Time']}, index_col='datetime')
sss
# colors
dark_blue = '#005b9a'
light_blue = '#00a2e1'
green = '#96bf23'

# build app
app = dash.Dash(__name__)
server = app.server
app.title='Lena River Monitoring'

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Img(src='/assets/moses_logo.png', style={'width': '30%'})
            ],
            className='header-image',
        ),
        html.Div(
            children=[
                html.H1(
                    "Lena River Monitoring", className='header-title'
                ),
                html.P(
                    children='Welcome to the Lena River Monitoring dashboard.'
                    ' Here you can check out the latest data from the Samoylov'
                    ' research station in Siberia, Russia.',
                    className='header-description',
                ),
            ],
            className='header',
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(                   # menu
                            children=[
                                html.Div(           # dropdown
                                    children=[
                                        html.Div(children='Select Parameter', className='menu-title'),
                                        dcc.Dropdown(
                                            id='select-y',
                                            options=[
                                                {'label': 'Temperature', 'value': 'Temperature (°C)'},
                                                {'label': 'Conductivity', 'value': 'Conductivity in situ (µS/cm)'},
                                            ],
                                            value='Temperature (°C)',
                                            clearable=False,
                                            multi=False,
                                            style={'width': '100%'},
                                            className='dropdown',
                                        ),
                                    ],
                                    style={'width': '20%'}
                                 ),
                                 html.Div(           # date range
                                     children=[
                                         html.Div(children='Select Date Range', className='menu-title'),
                                         dcc.DatePickerRange(
                                             id='date-range',
                                             min_date_allowed=tc.DateTime.min().date(),
                                             max_date_allowed=tc.DateTime.max().date(),
                                             start_date=tc.DateTime.min().date(),
                                             end_date=tc.DateTime.max().date(),
                                             display_format='DD.MM.YYYY',
                                             className='dropdown'
                                        ),
                                    ],
                                     style={'width': '50%'}
                                 ),
                            ],
                            className='menu'
                        ),
                        dcc.Graph(
                            id='time-series',
                        ),
                    ],
                    className='card',
                ),
                html.Div(
                    children=[
                        dcc.Graph(id='discharge-over-year'),
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.Div(id='slider-title', className='menu-title'),
                                        dcc.Slider(
                                            id='year-slider',
                                            min = years.min(),
                                            max = years.max(),
                                            value = 2020,
                                            marks = {str(year): str(year) for year in years[4::10]},
                                            step = 1,
                                            className='slider',
                                        ),
                                    ],
                                    style={'width': '80%'}
                                ),
                            ],
                            className='slider-menu',
                        ),
                    ],
                    className='card',
                ),
            ],
            className='wrapper',
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.P('For more information about the MOSES project please visit the AWI homepage.'),
                    ],
                    className='footer-text'
                ),
            ],
            className='footer',
        )
    ]
)


@app.callback(
    [
        Output(component_id='time-series', component_property='figure'),
        Output('discharge-over-year', 'figure'),
        Output('slider-title', 'children')
    ],
    [
        Input('select-y', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),
        Input('year-slider', 'value'),
    ]
)


def update_figures(y_selected, start_date, end_date, discharge_year):
    name = y_selected.split()[0]

    data = tc.copy()
    mask = (
       (data.DateTime >= start_date)
        & (data.DateTime <= end_date)
    )
    data = data[mask]

    # fist plot
    tc_plot = px.line(data, x='DateTime', y=data[y_selected])
    tc_plot.update_traces(line_color='#96bf23')
    tc_plot.update_layout(xaxis={'title': 'Date'},
                      title={
                          'text': '{} Time Series measured at Samoylov research station'.format(name),
                          'xanchor': 'center',
                          'x': 0.5,
                          'y': 0.94,
                      },
                      font_color='#005b9a'
                     )

    # second plot
    discharge_over_year = go.Figure()
    years = df.index.year.unique()
    colors = sns.color_palette('RdBu_r', len(years))
    for i, year in enumerate(years):
        discharge_over_year.add_trace(go.Scatter(x = df.loc[str(year)].index.dayofyear, y = df.loc[str(year)].discharge,
                                 line=dict(width = 0.5, color='rgb'+str(colors[i]),
                                          ),
                                                 meta=str(year),
                                hovertemplate='<b>%{meta}</b><extra></extra>',
                                                 text='adf'
                                ))
    discharge_over_year.add_trace(go.Scatter(x = df.loc[str(discharge_year)].index.dayofyear, y = df.loc[str(discharge_year)].discharge,
                             line=dict(width = 1.5, color='black')))

    # discharge_over_year.add_vline(x=today) # not working for some reason
    discharge_over_year.add_shape(type='line', x0=today, x1=today, y0=0, y1=1, yref='paper',
                                    line=dict(color=light_blue, width=.5))
    discharge_over_year.add_annotation(x=today, y=0.9, yref='paper',
            text="today",
            showarrow=False,
            xanchor='right',
            textangle=270,
            font={'color': light_blue},
            arrowhead=1,
            opacity=.6)
    discharge_over_year.update_layout(title={
                          'text': 'Discharge over the year',
                          'xanchor': 'center',
                          'x': 0.5,
                          'y': 0.85,
                          },
                          font_color='#005b9a',
                         xaxis_title = 'Day of Year', yaxis_title = 'Discharge [m³/s]',
                         showlegend=False)
    colorbar_trace  = go.Scatter(x=[None],
                                 y=[None],
                                 mode='markers',
                                 marker=dict(
                                     colorscale='RdBu_r',
                                     showscale=True,
                                     cmin=1936,
                                     cmax=2021,
                                     colorbar=dict(thickness=15, outlinewidth=0, title='Year') # change label when changig parameter
                                 ),
                            )
    discharge_over_year.add_trace(colorbar_trace)

    # display selected year from slider
    slider_title = 'Drag the slider to change the highlighted year (currently selected: {})'.format(discharge_year)

    return tc_plot, discharge_over_year, slider_title



if __name__ == "__main__":
    app.run_server(debug=True, port=3000)

print(today)
