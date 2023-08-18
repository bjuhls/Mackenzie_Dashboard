import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash import callback_context
import numpy as np
import pandas as pd
import xlsxwriter
from scipy.stats import linregress
from scipy.optimize import curve_fit
import datetime

import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from multipage_app import app

import os

#from login_information import password as pw


# import data
df = pd.read_csv('data/DUCCEM_sampling_list.csv', parse_dates=['Date'], na_values='n.a.', sep=";")
df['Day of Year'] = df.Date.dt.dayofyear
df['Year'] = df.Date.dt.year
df['Month'] = df.Date.dt.month

dis = pd.read_csv('data/Mackenzie_ArcticRedRiver_Version_20230809.csv',
    parse_dates=['date'], index_col='date', sep=";"
)
df['Discharge'] = dis.loc[list(df.Date)].discharge.values
param_info = pd.read_csv('data/Parameter_Info_Mackenzie.csv', index_col='Name')

# define columns to use
not_used = set()
remove_str = ['ID', 'QF', 'cations and anions', 'cuvette lenght', 'Instrument']
for c in df.columns:
    for r in remove_str:
        if r in c:
            not_used.add(c)
used_cols = sorted([col for col in df.columns if col not in not_used], key=str.casefold)


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

# import parameter information
info = pd.read_csv('data/Parameter_Info_Mackenzie.csv')

ts_mask = info['For Timeseries']=='Yes'
sc_mask = info['For Scatter']=='Yes'
new_label_mask = info['Renamed (unit)'].isnull()==False

ts_alphabetic = np.argsort([str.casefold(i) for i in info.Name[ts_mask]])

labels = info.Name.copy()
labels[new_label_mask] = info['Renamed (unit)'][new_label_mask]

# check if files match
if sum(df.columns.values != info.Name.values) > 0:
    raise ValueError('The columns of the data file and the Names in the info file do not match!')

# set values below QF to np.nan
#ii = range(45,79,2) # ion indices, modify when ions are added
#for i, col in zip(ii, df.columns[ii]):
#    df.loc[df.iloc[:, i] < df.iloc[:, i+1], col] = np.nan

# login status
login = False



# define colors
clinfit = 'royalblue'
clogfit = 'green'
cpowfit = 'firebrick'
theme = '#3d837f'
theme_second = '#dbe7f5'
muted_blue = 'royalblue'
brick_red = 'crimson'
darklink = '#373a3c'


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
    y1_info = info[info.Name==first_y].Info
    y2_info = info[info.Name==second_y].Info
    y1_name = info[info.Name==first_y]['Renamed (unit)'].values[0]
    y2_name = info[info.Name==second_y]['Renamed (unit)'].values[0]
    y1_unit = y1_name.split(' (')[1][:-1]
    y2_unit = y2_name.split(' (')[1][:-1]

    if y1_unit in ['unitless']:
        y1_unit=''
    if y2_unit in ['unitless']:
        y2_unit=''


    # handle data
    data = df.copy()
    #ts = pd.Timestamp(data.Datetime)
    time_mask = (pd.to_datetime(data.Date.dt.date) >= datetime.datetime.strptime(start, '%Y-%m-%d')) & (pd.to_datetime(data.Date.dt.date) <= datetime.datetime.strptime(end, '%Y-%m-%d'))
    data = data[time_mask]
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=data.Date, y=data[first_y],
            mode='lines+markers',
            name=y1_name.split('(')[1].split(')')[0],
            hovertemplate= '%{text}' + '<extra></extra>',
            text= ['<b>{}</b> <br> {} {}'.format(y1_name.split(' (')[0], i, y1_unit) for i in data[first_y]]#y1_name.split('(')[1].split(')')[0]]*len(data[first_y])
        ),
        secondary_y=False,
    )
    # print(y1log, type(y1log))

    fig.add_trace(
        go.Scatter(x=data.Date, y=data[second_y],
            mode='lines+markers',
            name=y2_name.split('(')[1].split(')')[0],
            hovertemplate= '%{text}' + '<extra></extra>',
            text= ['<b>{}</b> <br> {} {}'.format(y2_name.split(' (')[0], i, y2_unit) for i in data[second_y]]
            # hovertemplate='%{y} <extra></extra>' + '%{text}',
            # text= [y2_name.split('(')[1].split(')')[0]]*len(data[second_y])
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title={'text': "Time Series", 'x': 0.5, 'y': 0.93},
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=10, l=10, r=10),
        hovermode="x"
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
    # print(first_y, y1_name)

    fig.update_yaxes(title_text=y1_name, color=muted_blue, secondary_y=False,
    type=y1type, showgrid=True, gridwidth=1) #, gridcolor='lightblue', zerolinecolor='lightblue')
    fig.update_yaxes(title_text=y2_name, color=brick_red, secondary_y=True,
    type=y2type) #, gridcolor='lightpink', zerolinecolor='lightpink')

    colors = [trace.line["color"] for trace in fig.data]
    # print(colors)
    if first_y is None:
        raise PreventUpdate
    else:
        return fig, y1style, y2style, y1_name, y2_name, y1_info, y2_info

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
        # Output('text-output', 'children'),
        Output('x-log', 'style'),
        Output('y-log', 'style'),
        Output('color-log', 'style'),
        Output('linfit-collapse', 'is_open'),
        Output('linfit-card', 'children'),
        Output('logfit-collapse', 'is_open'),
        Output('logfit-card', 'children'),
        Output('powfit-collapse', 'is_open'),
        Output('powfit-card', 'children')
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
    # x_name = x_selected.split()[0]
    # y_name = y_selected.split()[0]

    x_name = info[info.Name==x_selected]['Renamed (unit)'].values[0]
    y_name = info[info.Name==y_selected]['Renamed (unit)'].values[0]
    c_name = info[info.Name==color]['Renamed (unit)'].values[0]

    x_unit = x_name.split(' (')[1][:-1]
    y_unit = y_name.split(' (')[1][:-1]
    c_unit = c_name.split(' (')[1][:-1]
    if x_unit in ['unitless', 'JJJ', 'MM', 'YYY']:
        x_unit=''
    if y_unit in ['unitless', 'JJJ', 'MM', 'YYY']:
        y_unit=''
    if c_unit in ['unitless', 'JJJ', 'MM', 'YYY']:
        c_unit=''                                 # not so beatiful..

    data = df.copy()
    
    time_mask = (pd.to_datetime(data.Date.dt.date) >= datetime.datetime.strptime(start, '%Y-%m-%d')) & (pd.to_datetime(data.Date.dt.date) <= datetime.datetime.strptime(end, '%Y-%m-%d'))
    data = data[time_mask]

    x=data[x_selected]
    y=data[y_selected]
    nan_mask = ~np.isnan(x) & ~np.isnan(y)
    x = x[nan_mask]
    y = y[nan_mask]

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
    color=c, color_continuous_scale='viridis',
    custom_data=[color]
    )

    scatter.update_traces(
        name='sample points',
        showlegend = True,
        hovertemplate=''.join([
            '<b>{}:</b> {} {}<br>'.format(x_name.split(' (')[0], '%{x}', x_unit),
            '<b>{}:</b> {} {}<br>'.format(y_name.split(' (')[0], '%{y}', y_unit),
            '<b>{}:</b> {} {}<br>'.format(c_name.split(' (')[0], '%{customdata[0]}', c_unit),
            '<extra></extra>'
        ])
    )


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


    # linear fit
    linfit = linregress(x, y)
    linfitcard = dbc.Card(
        className='fit-card',
        children=[
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

    if lin_fit==['on']:
        lin_collapse=True
        scatter.add_trace(go.Scatter(
            x=np.sort(x),
            y=linfit.slope*np.sort(x)+linfit.intercept,
            mode='lines',
            name='linear fit',
            line=dict(color=clinfit, dash='dash'),
            hoverinfo='skip'
        )
        )

    else:
        lin_collapse=False

    # logarithmic fit
    def logfit(x, m, n):
        return m * np.log(x) + n

    logfitcard_failed = dbc.Card(
        className='fit-card',
        children=[
            dbc.CardHeader(html.H6('Logarithmic Fit', style={'font-weight': 'bold', 'color':clogfit, 'text-align':'center'}),
                ),
            dbc.CardBody(
                [
                    html.P('y = m \U000022C5 log (x) + n', className='fit-text', style={'color': clogfit}),
                    html.P('The calculation of a logarithmic fit is mathematically not possible for the selected parameters.',
                        style={'text-align':'center'})
                ]
            )
        ],
        color="success",
        outline=True
        ),

    try:
        lpopt, lpcov = curve_fit(logfit, x, y)
        lperr = np.sqrt(np.diag(lpcov))
        res = y - logfit(x, *lpopt)
        sqsum_res = np.sum(res**2)
        sqsum_tot = np.sum((y-np.mean(y))**2)
        Rsq_log = 1 - sqsum_res/sqsum_tot

    except RuntimeError:
        logfitcard = logfitcard_failed
        lperr=[np.inf, np.inf] # this is messy!

    if lperr[0]+lperr[1] != np.inf:

        logfitcard = dbc.Card(
            className='fit-card',
            children=[
                dbc.CardHeader(html.H6('Logarithmic Fit', style={'font-weight': 'bold', 'color':clogfit, 'text-align':'center'}),
                    ),
                dbc.CardBody(
                    [
                        html.P('y = m \U000022C5 log (x) + n', className='fit-text', style={'color': clogfit}),
                        html.P(f'm = {lpopt[0]:.2f} ± {lperr[0]:.2f}', className='fit-text'),
                        html.P(f'n = {lpopt[1]:.2f} ± {lperr[1]:.2f}', className='fit-text'),
                        html.P(f'R\U000000B2 = {Rsq_log:.2f}', className='fit-text')
                    ]
                ),
                ],
                color="success",
                outline=True
            ),

    else:
        logfitcard = logfitcard_failed

    if log_fit == ['on']:
        log_collapse=True

        if lperr[1] != np.inf:
            scatter.add_trace(go.Scatter(x=np.sort(x), y=logfit(np.sort(x), *lpopt), mode='lines', name='logarithmic fit',
                line=dict(color=clogfit, dash='dot'), hoverinfo='skip'
                ))
    else:
        log_collapse=False


    # power fit
    x=data[x_selected]
    y=data[y_selected]
    def pow(x, a, b, c):
        return a * np.power(x, b) + c

    powfitcard_failed = dbc.Card(
        className='fit-card',
        children=[
            dbc.CardHeader(html.H6('Power Fit', style={'font-weight': 'bold', 'color':cpowfit, 'text-align':'center'})),
            dbc.CardBody(
            # className='internal-card',
            children=[
                html.P('y = a \U000022C5 x\U00001D47 + c', className='fit-text', style={'color': cpowfit}),
                html.P('The calculation of a power fit is mathematically not possible for the selected parameters.',
                    style={'text-align':'center'})
            ],
            )
        ],
        color="danger",
        outline=True
    ),

    try:
        ppopt, ppcov = curve_fit(pow, x[nan_mask], y[nan_mask])
        pperr = np.sqrt(np.diag(ppcov))
        res = y - pow(x, *ppopt)
        sqsum_res = np.sum(res**2)
        sqsum_tot = np.sum((y-np.mean(y))**2)
        Rsq_pow = 1 - sqsum_res/sqsum_tot

    except RuntimeError:
        powfitcard = powfitcard_failed

        pperr = [np.inf, np.inf] # again messy!




    if pperr[0]+pperr[1] != np.inf:

        powfitcard = dbc.Card(
            className='fitcards-card',
            children=[
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
    else:
        powfitcard = powfitcard_failed

    if pow_fit == ['on']:
        pow_collapse=True

        if pperr[0]+pperr[1] != np.inf:
            scatter.add_trace(go.Scatter(x=np.sort(x), y=pow(np.sort(x), *ppopt), mode='lines', name='power fit', line=dict(color=cpowfit, dash='dashdot'), hoverinfo='skip'))

    else:
        pow_collapse=False

    scatter.update_layout(
        coloraxis_colorbar={'title':c_name, 'tickprefix':tp, 'titleside':'right', 'thickness': 20},
        title={'text': f"{y_name.split('(')[0]} vs. {x_name.split('(')[0]}", 'x': 0.5, 'y': 0.93},
        legend={'x':0.02, 'y':0.98, 'xanchor':'left', 'yanchor':'top'},
        margin=dict(b=65, r=0),
    )



    scatter.update_yaxes(title_text=y_name)
    scatter.update_xaxes(title_text=x_name)

    # scatter.show(config = {'displayModeBar': False})


    # return scatter, fitcards, xstyle, ystyle, cstyle, lin_collapse, linfitcard, log_collapse, logfitcard
    return scatter, xstyle, ystyle, cstyle, lin_collapse, linfitcard, log_collapse, logfitcard, pow_collapse, powfitcard


# Slideshow

@app.callback(
    [
        Output("img-description", 'children'),
        Output("img-slide", 'src'),
        Output('img-slide', 'title')
        # Output('image-counter', 'children')
    ],
    [
        Input('btn_prev', 'n_clicks'),
        Input('btn_next', 'n_clicks')
    ],
    prevent_initial_call=True
)

def slide(prev_clicks, next_clicks):

    # image_list = [
    #     'assets/slideshow1.png',
    #     'assets/slideshow2.png',
    #     'assets/map_example.png'
    # ]
    #
    # image_descriptions = [
    #     'This example image shows a part of the Lena Delta in bright colors.',
    #     'This example image shows the whole Lena Delta in bright colors.',
    #     'This example image is a screenshot from Google Maps. It would be more convenient if all images had the same height though.'
    # ]

    image_list = os.listdir('assets/Pictures/compressed')
    image_descriptions = [str.split(i, 'png')[0] for i in image_list]
    rights = [str.split(i, '. ')[-1] for i in image_descriptions]



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

    return image_descriptions[n], f'assets/Pictures/compressed/{image_list[n]}', rights[n] #, f'{n}/{len(image_list)}'
def toggle_collapse(n, is_open):
    if n:
        return not is_open,# {
        #     'margin-bottom':'1px',
        #     'margin-left': '-10px',
        #     'margin-right': '-10px',
        #     'border': '2px',
        # }
    return is_open,# {'background-color': 'white',
    #     'color': 'blue',
    #     'border': '0px',
    #     'margin-bottom': '2px'
    # }
