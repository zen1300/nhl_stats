import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State

from app import app
from layouts import team_stats

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])

index_layout = html.Div([
    dcc.Link('Team Stats', href='/team-stats'),
    dcc.Link('Player Stats', href='player-stats'),
    dcc.Link('Game Stats', href='game-stats'),
], style={'textAlign': 'center'})


@app.callback(
    output=[Output('page-content', 'children')],
    inputs=[Input('url', 'pathname')]
)
def navigate_page(pathname):
    if pathname == '/team-stats':
        return [team_stats.team_layout]
    # elif pathname == 'player-stats':
    #     return player_layout
    # elif pathname == 'game-stats':
    #     return game_layout
    else:
        return [index_layout]


if __name__ == '__main__':
    app.run_server(debug=True)
