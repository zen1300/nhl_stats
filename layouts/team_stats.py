import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_table
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd
import numpy as np
import sqlite3
from sklearn import preprocessing

from app import app
import values

# plotly defaults to only ~10 unique colors then repeats them
# create a new list of 48 unique colors to prevent repeats
COLORS = px.colors.qualitative.Dark24 + px.colors.qualitative.Light24

# load data options for graphs
SEASONS = [f'{year}' for year in range(1995, 2020)]
TEAMS = sorted(list(values.recent_teams_by_name.keys()))
TEAMS.remove('Phoenix Coyotes')
OPPONENT = TEAMS.copy()
OPPONENT.insert(0, 'All Teams')
GAME_TYPE = ['Full Season', 'Home', 'Away']

# load api database data for season level statistics
with sqlite3.connect('../nhl_stats.db') as connection:
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM team_season_stats')
    DATA = pd.read_sql_query('SELECT * FROM team_season_stats', connection)

DATA = DATA.sort_values(by=['Season', 'Team'])
STATS = [i for i in DATA.columns if i not in ['Season', 'Team', 'Games Played']]

# load api database data for game level statistics
with sqlite3.connect('../nhl_stats.db') as connection:
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM team_season_stats')
    GAME_DATA = pd.read_sql_query('SELECT * FROM game_stats_teams', connection)

GAME_DATA = GAME_DATA.sort_values(by=['Season', 'Team'])
GAME_STATS = [i for i in GAME_DATA.columns if i not in
              ['Season', 'Game Type', 'Game Number', 'Home', 'Away', 'Team', 'Game Time']]

team_layout = html.Div([
    # Page Links
    html.Div([
        html.Div([
            dcc.Link('Home Page', href='/'),
        ], style={'display': 'inline-block'}),
        html.Div([
            dcc.Link('Player Stats', href='/player-stats')
        ], style={'display': 'inline-block'}),
        html.Div([
            dcc.Link('Game Stats', href='/game-stats')
        ], style={'display': 'inline-block'})
    ], style={'textAlign': 'center'}),

    # Full Season level Data Table
    html.Div([
        dash_table.DataTable(
            id='team-stat-table',
            columns=[{'name': i, 'id': i} for i in DATA.columns],
            data=DATA.to_dict('records'),
            page_size=50,
            page_action='native',
            fixed_rows={'headers': True},
            style_cell={'minWidth': 95, 'width': 95, 'maxWidth': 95, 'height': 'auto', 'whiteSpace': 'normal'},
            style_table={'height': '500px', 'overflowY': 'auto', 'overflowX': 'auto', 'width': 'auto'},
            filter_action='native',
            sort_action='native',
            sort_mode='multi',
            row_selectable='multi',
            selected_rows=[i for i in range(len(DATA))],
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )
    ]),
    html.Hr(),

    # All Team Data
    html.Div([
        html.Div([
            html.H6('View the time series data for all teams for the selected stat.')
        ], style={'textAlign': 'center'}),
        html.Div([
            dcc.Dropdown(
                id='team-single-stat',
                options=[{'label': i, 'value': i} for i in DATA.columns if i not in ['Season', 'Team', 'Games Played']],
                value='Points',
                clearable=False,
            ),
        ], style={'display': 'inline-block', 'width': '20%'}),
    ], style={'textAlign': 'center'}),
    html.Div([
        dcc.Graph(id='team-single-stat-fig')
    ]),
    html.Hr(),

    # Individual Team Stats
    html.Div([
        html.Div([
            html.H6('View the time series data for one team and multiple stats.'),
            html.H6('Can optionally scale all stats from 0 to 1 for visualization.'),
        ], style={'textAlign': 'center'}),
        html.Div([
            html.Div([
                html.Label('Team: ')
            ], style={'display': 'inline-block', 'width': '10%'}),
            html.Div([
                dcc.Dropdown(
                    id='team-team-select',
                    options=[{'label': i, 'value': i} for i in TEAMS],
                    value='Anaheim Ducks',
                    clearable=False,
                ),
            ], style={'display': 'inline-block', 'width': '20%'}),
            html.Div([
                html.Label('Stats: ')
            ], style={'display': 'inline-block', 'width': '10%'}),
            html.Div([
                dcc.Dropdown(
                    id='team-multi-stat',
                    options=[{'label': i, 'value': i} for i in STATS],
                    value='Points',
                    clearable=True,
                    multi=True
                )
            ], style={'display': 'inline-block', 'width': '20%'}),
            html.Div([
                html.Label('Scale Data: ')
            ], style={'display': 'inline-block', 'width': '10%'}),
            html.Div([
                daq.BooleanSwitch(
                    id='team-scale-switch',
                    on=False
                )
            ], style={'display': 'inline-block'})
        ]),
    ], style={'textAlign': 'center'}),
    html.Div([
        dcc.Graph(id='team-multi-stat-fig')
    ]),

    # Team Season Game Stats
    html.Div([
        html.Div([
            html.H6('View both the game-specific data and the running average season data for one team.'),
        ], style={'textAlign': 'center'}),
        html.Div([
            html.Div([
                html.Label('Season: ')
            ], style={'display': 'inline-block', 'width': '10%'}),
            html.Div([
                dcc.Dropdown(
                    id='team-season-season',
                    options=[{'label': i, 'value': i} for i in SEASONS],
                    value='2019',
                    clearable=False,
                ),
            ], style={'display': 'inline-block', 'width': '20%'}),
            html.Div([
                html.Label('Team: ')
            ], style={'display': 'inline-block', 'width': '10%'}),
            html.Div([
                dcc.Dropdown(
                    id='team-season-team',
                    options=[{'label': i, 'value': i} for i in TEAMS],
                    value='Anaheim Ducks',
                    clearable=False,
                ),
            ], style={'display': 'inline-block', 'width': '20%'}),
            html.Div([
                html.Label('Opponent: ')
            ], style={'display': 'inline-block', 'width': '10%'}),
            html.Div([
                dcc.Dropdown(
                    id='team-season-opponent',
                    options=[{'label': i, 'value': i} for i in OPPONENT],
                    value='All Teams',
                    clearable=False,
                ),
            ], style={'display': 'inline-block', 'width': '20%'}),
        ]),
        html.Div([
            html.Div([
                html.Label('Game Type: ')
            ], style={'display': 'inline-block', 'width': '10%'}),
            html.Div([
                dcc.Dropdown(
                    id='team-season-gametype',
                    options=[{'label': i, 'value': i} for i in GAME_TYPE],
                    value='Full Season',
                    clearable=False,
                ),
            ], style={'display': 'inline-block', 'width': '20%'}),
            html.Div([
                html.Label('Stat: ')
            ], style={'display': 'inline-block', 'width': '10%'}),
            html.Div([
                dcc.Dropdown(
                    id='team-season-stat',
                    options=[{'label': i, 'value': i} for i in GAME_STATS],
                    value='Goals',
                    clearable=False,
                )
            ], style={'display': 'inline-block', 'width': '20%'}),
        ]),
    ], style={'textAlign': 'center'}),
    html.Div([
        dcc.Graph(id='team-season-stat-fig')
    ]),
])


# callback for updating the figure responsible for displaying single stat for all teams
@app.callback(
    output=[Output('team-single-stat-fig', 'figure')],
    inputs=[Input('team-single-stat', 'value')]
)
def all_team_stats(stat):
    # Query and load api data
    # Necessary? Just grab full table? Or leave to allow for season / team
    # specific queries in future?
    query = """
        SELECT * FROM team_season_stats 
        WHERE Season IN (%s) 
        AND Team IN (%s)
        """ % (','.join('?' * len(SEASONS)), ','.join('?' * len(TEAMS)))
    params = SEASONS + TEAMS

    with sqlite3.connect('../nhl_stats.db') as c:
        df = pd.read_sql_query(query, con=c, params=params)

    fig = go.Figure()
    # add scatter plot for every team of given stat
    for team in TEAMS:
        _df = df[df['Team'] == team].dropna(subset=['Team'])
        fig.add_trace(
            go.Scatter(
                x=_df['Season'],
                y=_df[stat],
                uid=team,
                name=team,
                mode='lines+markers',
                marker={
                    'color': f'rgba{values.team_colors[team][0]}',  # team primary color
                    'line': {
                        'color': f'rgba{values.team_colors[team][1]}',  # team secondary color
                        'width': 2
                    }
                }
            )
        )
    # do not update the legend selections when changing the data (uirevision = True)
    # allows for filtering of legend items to stay when changing data
    fig.update_layout(
        height=600,
        legend={'uirevision': True},
        template='plotly_white'
    )

    return [fig]


# callback for updating the figure that compares multiple stats for a single team
@app.callback(
    output=[Output('team-multi-stat-fig', 'figure')],
    inputs=[
        Input('team-team-select', 'value'),
        Input('team-multi-stat', 'value'),
        Input('team-scale-switch', 'on'),
    ]
)
def all_team_stats(team, stats, scale):
    if stats:
        # dash will pass a single stat as a string and multiples as list
        # ensure standard data type
        if isinstance(stats, str):
            stats = [stats]

        # query and load all season data for selected team
        query = """
            SELECT * FROM team_season_stats 
            WHERE Season IN (%s) 
            AND Team=?
            """ % ','.join('?' * len(SEASONS))
        params = SEASONS + [team]

        with sqlite3.connect('../nhl_stats.db') as c:
            df = pd.read_sql_query(query, con=c, params=params)

        # Visualization not ideal for comparing stats of different scale (e.g. GAA and PK%)
        # Standardize each stat to 0->1 for better visual comparisons
        if scale:
            scaler = preprocessing.MinMaxScaler()
            # keep original df so hovertext can still display un-scaled data
            scaled = df.copy()
            scaled[stats] = scaler.fit_transform(scaled[stats].values)

        hovertext = [[f'{i}: {j}' for j in df[i].values.tolist()] for i in stats]
        fig = go.Figure()
        # add scatter plot for every selected stat
        for index, stat in enumerate(stats):
            if scale:
                df = scaled

            fig.add_trace(
                go.Scatter(
                    x=df['Season'],
                    y=df[stat],
                    uid=stat,
                    name=stat,
                    mode='lines',
                    marker={'color': COLORS[index]},
                    hovertext=hovertext[index],
                    hoverinfo='text'
                )
            )

        # do not update the legend selections when changing the data (uirevision = True)
        # allows for filtering of legend items to stay when changing data
        fig.update_layout(
            height=600,
            legend={'uirevision': True},
            template='plotly_white'
        )

        return [fig]
    return [dash.no_update]


# callback that updates the figure that shows per-game season data
@app.callback(
    output=[Output('team-season-stat-fig', 'figure')],
    inputs=[
        Input('team-season-season', 'value'),
        Input('team-season-team', 'value'),
        Input('team-season-opponent', 'value'),
        Input('team-season-gametype', 'value'),
        Input('team-season-stat', 'value'),
    ]
)
def all_team_stats(season, team, opponent, gametype, stat):
    # query and get api data for chosen team and season
    query = """
        SELECT * FROM game_stats_teams 
        WHERE Season=:season 
        AND Team=:team
        """
    params = {'season': season, 'team': team}

    # further filter query for only home/away data
    if gametype == 'Home':
        query += ' AND Home=:team'
    elif gametype == 'Away':
        query += ' AND Away=:team'

    # further filter query for games against specific opponent
    if opponent != 'All Teams':
        query += ' AND (Home=:opponent OR Away=:opponent)'
        params['opponent'] = opponent

    with sqlite3.connect('../nhl_stats.db') as c:
        df = pd.read_sql_query(query, con=c, params=params)

    # set hover text for game specific data
    # TODO update hovertext to specify 'individual' stat
    cols = ['Home', 'Away', 'Game Time', stat]
    df['Game Time'] = pd.to_datetime(df['Game Time'], infer_datetime_format=True)
    hovertext = df[cols].to_dict('records')
    hovertext = [''.join([f'{j}: {i[j]}<br>' for j in i]) for i in hovertext]
    # create bool mask for color coding points for home/away games
    home_bool = np.where(df['Home'] == team, True, False).astype('int')

    fig = go.Figure()
    # Add scatter plot for game specific data
    fig.add_trace(
        go.Scatter(
            x=[i for i in range(1, len(df))],
            y=df[stat],
            uid=f'Individual {stat}',
            name=f'Individual {stat}',
            mode='lines+markers',
            marker={
                'color': home_bool,
                'colorscale': [[0, 'red'], [1, 'green']]
            },
            hovertext=hovertext,
            hoverinfo='text',
        )
    )

    # recompute stat to a running average clipped to 2 decimal points
    df[stat] = df[stat].expanding().mean()
    df[stat] = df[stat].round(2)
    # TODO update hovertext to specify 'average' data
    hovertext = df[cols].to_dict('records')
    hovertext = [''.join([f'{j}: {i[j]}<br>' for j in i]) for i in hovertext]

    fig.add_trace(
        go.Scatter(
            x=[i for i in range(1, len(df))],
            y=df[stat],
            uid=f'Average {stat}',
            name=f'Average {stat}',
            mode='lines+markers',
            marker={
                'color': home_bool,
                'colorscale': [[0, 'red'], [1, 'green']]
            },
            hovertext=hovertext,
            hoverinfo='text',
        )
    )

    # do not update the legend selections when changing the data (uirevision = True)
    # allows for filtering of legend items to stay when changing data
    fig.update_layout(
        height=600,
        legend={'uirevision': True},
        template='plotly_white'
    )

    return [fig]
