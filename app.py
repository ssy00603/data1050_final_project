import dash
import pandas as pd
import datetime
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from dash import dash_table
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, FormatStrFormatter
import numpy as np


app = dash.Dash(__name__)

server = app.server

df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
states = sorted(df.state.unique())
days = ['last 7 days', 'last 14 days', 'last 30 days']

df_line = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv")
df_line=df_line.loc[df_line.continent.isin(["Asia", 'Europe', "Africa", "North America", "South America", "Oceania"])].groupby(["date", "continent"]).sum().reset_index()



app.layout = html.Div(className = 'main', children = [
    # Add title
    html.H2(children="Covid-19 Dashboard", style = {'text-align':'center'}),

    # Add live date
    dcc.Interval(
        id='interval-component',
        interval=5000,
        n_intervals=0
    ),

    html.H4(children="This web page is an overview of the daily cases, deaths, and trends of COVID-19 in the United States. COVID-19 is an illness caused by coronavirus and similar to the common cold. But the symptom of COVID-19 can be severe and causes millions of deaths. So it is important for us to constantly track the spreads of COVID-19", style = {'text-align':'center'}),
    
    html.H4(children="Cases Trends"),
    html.P(children="The first chart shows how daily new cases have changed in each state of the country. The exact state and number of days to display can be chosen below. The trends of total cases and deaths are shown below as well."),
    
    # Add tabs
    dcc.Tabs(id="tabs-inline", value='tab-1', children=[
        # Add tab of New Cases
        dcc.Tab(label='New Cases by States', value='tab-1', children=[
            # Choose states
            html.Div(className = 'dropdown-class', children = [
            dcc.Dropdown(
                id="dropdown",
                options=[{"label": x, "value": x} for x in states],
                value=states[0],
                clearable=False,
            ),
            # Choose day intervals
            dcc.Dropdown(
                id="dropdown-days",
                options=[{"label": x, "value": x} for x in days],
                value=days[0],
                clearable=False,
            )]),
            # Display bar plot
            dcc.Graph(id="bar-chart-new")
        ]),

        # Add tab of Total Cases
        dcc.Tab(label='Total Cases', value='tab-2', children=[
            # Display bar plot
            dcc.Graph(id="bar-chart-total")
        ]),

        # Add tab of Deaths
        dcc.Tab(label='Deaths', value='tab-3', children=[
            # Display bar plot
            dcc.Graph(id="bar-chart-death")
        ])]),

        html.H4(children="Cases Maps"),
        html.P(children="The first map shows the number of vaccinations in each state. The second map shows the total confirmed cases in each state."),

        html.Div(className = 'maps',children = [
        # Display map
        dcc.Graph(id="map-vaccine"),

        # Display map
        dcc.Graph(id="map-confirm-case")]),
        
        html.H4(children="Top Cases"),
        html.P(children="The first chart shows the states with highest number of confirmed case. The second line plot shows the continents with highest number of confirmed case."),

        html.Div(className='lastrow',children = [
        html.Div(className = 'piechart',children = [
        dcc.Dropdown(
            id = 'drop-down',
            options = [
                {'label':'Top 5', 'value':'Top 5'},
                {'label': 'Top 10', 'value':'Top 10'},
                {'label': 'Top 15', 'value':'Top 15'}
            ],
            value = 'Top 5',
            clearable=False
        ),

        dcc.Tabs(
            id = 'cases-deaths-tabs',
            value = 'cases',
            children = [
                dcc.Tab(id = 'case-tab',label = 'Cases', value = 'cases'),
                dcc.Tab(id = 'death-tab',label = 'Deaths', value = 'deaths')
            ]
        ),

        html.Div(id = 'dd-tab-output-container'),
        ]),
        dcc.Graph(id = 'line-graph',
            figure = px.line(df_line, x='date', y='total_cases', color='continent',labels = {'continent':'Continents'},
            title='Global Confirmed Cases by Continent').update_layout({'plot_bgcolor':'white'}),
        ),       
    ]),
    dcc.Slider(
        id='line-graph-slider',
        min=1,
        max=24,
        step=1,
        value=24,
        marks={
            1: '1 month',
            6: '6 months',
            12: '1 year',
            18: '1 year 6 months',
            24: '2 years'
        }
    )     
])




@app.callback(
    Output('bar-chart-new', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input("dropdown", "value"),
    Input("dropdown-days", "value"))

def bar_plot_days(n_clicks, states, days):
    df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
    # Add previous cases column
    df['prev_cases'] = df.groupby('state')['cases'].shift().fillna(0)
    # Add new cases column
    df['new cases'] = df['cases'] - df['prev_cases']

    # Choose display day interval
    if days == 'last 7 days':
        df = df[df["state"] == states].iloc[-1:-8:-1][::-1]
    if days == 'last 14 days':
        df = df[df["state"] == states].iloc[-1:-15:-1][::-1]
    else:
        df = df[df["state"] == states].iloc[-1:-31:-1][::-1]

    # Plot line with bar plot
    fig = px.line(df, x="date", y="new cases")
    fig.add_bar(x=df["date"], y=df["new cases"], marker=dict(color="Blue", opacity=0.3), showlegend=False)

    fig.update_layout(
    plot_bgcolor="white",
    xaxis_title="Date",
    yaxis_title="Number of New Cases"
    )

    return fig


@app.callback(
    Output('bar-chart-total', 'figure'),
    Input('interval-component', 'n_intervals'))

def bar_plot_total(n_clicks):
    df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
    df = df.groupby('date').sum().reset_index()
    
    # Plot line with bar plot
    fig = px.line(df, x="date", y="cases")
    fig.add_bar(x=df["date"], y=df["cases"], marker=dict(color="Blue", opacity=0.3), showlegend=False)

    fig.update_layout(
    plot_bgcolor="white",
    xaxis_title="Date",
    yaxis_title="Number of Total Cases"
    )

    return fig


@app.callback(
    Output('bar-chart-death', 'figure'),
    Input('interval-component', 'n_intervals'))

def bar_plot_death(n_clicks):
    df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
    df = df.groupby('date').sum().reset_index()
    
    # Plot line with bar plot
    fig = px.line(df, x="date", y="deaths")
    fig.add_bar(x=df["date"], y=df["deaths"], marker=dict(color="Blue", opacity=0.3), showlegend=False)

    fig.update_layout(
    plot_bgcolor="white",
    xaxis_title="Date",
    yaxis_title="Number of Death"
    )

    return fig

@app.callback(
    Output('map-vaccine', 'figure'),
    Input('interval-component', 'n_intervals'))

def map_vaccine(n):
    df_vaccine = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv')
    df_vaccine = df_vaccine[['date', 'location', 'total_vaccinations']]
    df_vaccine = df_vaccine.groupby('location').sum().reset_index()

    df_state_code = pd.read_csv('https://raw.githubusercontent.com/jasonong/List-of-US-States/master/states.csv')

    df_state_vaccine = df_state_code.merge(df_vaccine, left_on='State', right_on='location')
    df_state_vaccine = df_state_vaccine[['State', 'Abbreviation', 'total_vaccinations']]

    # Plot map
    fig = px.choropleth(df_state_vaccine,
                        locations='Abbreviation',
                        color='total_vaccinations',
                        color_continuous_scale='Teal',
                        hover_name='State',
                        locationmode='USA-states',
                        labels={'total_vaccinations':'Number of Vaccinations'},
                        scope='usa')

    # Hide line between states
    fig.update_traces(marker_line_width=0)

    # Add State abbreviation
    fig.add_scattergeo(locations=df_state_vaccine['Abbreviation'],
                        locationmode='USA-states',
                        text=df_state_vaccine['Abbreviation'],
                        mode='text',
                        hoverinfo='none')

    fig.update_layout(
        title={'text':'Total Vaccinations by State',
            'xanchor':'center',
            'yanchor':'top',
            'x':0.5})

    return fig


@app.callback(
    Output('map-confirm-case', 'figure'),
    Input('interval-component', 'n_intervals'))

def map_confirm_case(n):
    df_state_code = pd.read_csv('https://raw.githubusercontent.com/jasonong/List-of-US-States/master/states.csv')
    df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
    df_confirm_case = df.merge(df_state_code, left_on='state', right_on='State')[['date', 'Abbreviation', 'cases']]
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    df_confirm_case = df_confirm_case[df_confirm_case['date'] == str(yesterday)]

    # Plot map
    fig = px.choropleth(df_confirm_case,
                        locations='Abbreviation',
                        color='cases',
                        color_continuous_scale='amp',
                        hover_name='Abbreviation',
                        locationmode='USA-states',
                        labels={'cases':'Number of Confirmed Cases'},
                        scope='usa')

    # Hide line between states
    fig.update_traces(marker_line_width=0)

    # Add State abbreviation
    fig.add_scattergeo(locations=df_confirm_case['Abbreviation'],
                        locationmode='USA-states',
                        text=df_confirm_case['Abbreviation'],
                        mode='text',
                        hoverinfo='none')

    fig.update_layout(
        title={'text':'Total Confirmed Cases by State',
            'xanchor':'center',
            'yanchor':'top',
            'x':0.5})
    
    return fig

@app.callback(
    Output('dd-tab-output-container','children'),
    [Input('interval-component','n_intervals'),
    Input('drop-down','value'),
    Input('cases-deaths-tabs','value')]
)

def render_piechart(interval,dropdown,tab):
    df_pie = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/live/us-counties.csv")
    case_x = df_pie.groupby('state')['cases'].sum()
    death_x = df_pie.groupby('state')['deaths'].sum()
    legend_title = dropdown + ' States'

    if tab == 'cases':
        if dropdown == 'Top 5':
            case_x = case_x.sort_values(ascending = False)[:5]
        if dropdown == 'Top 10':
            case_x = case_x.sort_values(ascending = False)[:10]
        if dropdown == 'Top 15':
            case_x = case_x.sort_values(ascending = False)[:15]
        case_figure = px.pie(data_frame=df_pie,values=case_x.values,names=case_x.keys(),color=case_x.keys(),hole=0.4)
        case_figure.update_layout(
        title={'text':'Confirmed Cases by Top States',
            'xanchor':'center',
            'yanchor':'top',
            'x':0.5}, legend_title_text = legend_title)
        return html.Div([
            dcc.Graph(
                id = 'case-graph',
                figure = case_figure
            )
        ])

    if tab == 'deaths':
        if dropdown == 'Top 5':
            death_x = death_x.sort_values(ascending = False)[:5]
        if dropdown == 'Top 10':
            death_x = death_x.sort_values(ascending = False)[:10]
        if dropdown == 'Top 15':
            death_x = death_x.sort_values(ascending = False)[:15]
        death_figure = go.Figure(data = [go.Pie(labels = death_x.keys(), values = death_x.values, hole = 0.4)])
        death_figure = px.pie(data_frame=df_pie,values=death_x.values,names=death_x.keys(),color=death_x.keys(),hole=0.4)
        death_figure.update_layout(
        title={'text':'Deaths by Top States',
            'xanchor':'center',
            'yanchor':'top',
            'x':0.5}, 
            legend_title_text = legend_title)
        return html.Div([
            dcc.Graph(
                id = 'death-graph',
                figure = death_figure
            )
        ])

@app.callback(
    Output('line-graph','figure'),
    [Input('line-graph-slider','value')]
)
def line_graph_update(value):
    df1=df_line
    df2 = df1.date.str.split(r"-", n=-1,expand=True)
    step_ind = list(np.zeros(4186))
    for i in range(4180):
        if df2[0][i] == '2020':
            step_ind[i] = int(df2[1][i])
        else:
            step_ind[i] = int(df2[1][i]) * 2
            
    df1["steo_ind"] = step_ind
    df1 = df1[df1.steo_ind<=value]
    return px.line(df1, x='date', y='total_cases', color='continent',labels = {'continent':'Continents'},title='Global Confirmed Cases by Continent').update_layout({'plot_bgcolor':'white'})


if __name__ == '__main__':
    app.run_server(debug=True)

