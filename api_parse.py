import json
import os

import requests

import utils
import values as v


def get_team_stats(team_id, season=20192020):
    r = requests.get(f'https://statsapi.web.nhl.com/api/v1/teams/{team_id}?expand=team.stats&season={season}')
    parsed = json.loads(r.text)

    season_values = parsed['teams'][0]['teamStats'][0]['splits'][0]['stat']
    season_values['Season'] = season

    season_ranks = parsed['teams'][0]['teamStats'][0]['splits'][1]['stat']
    season_ranks['Season'] = season

    return season_values, season_ranks


def get_player_stats(player_id, stats_by, season=20192020):
    r = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{player_id}/stats?stats={stats_by}&season={season}')
    parsed = json.loads(r.text)
    players = utils.players_by_id(os.getcwd() + '/NHL_players.xlsx')

    if stats_by == 'homeAndAway':
        values = _home_and_away(parsed)
        values[0]['Player'] = players[player_id]
        values[1]['Player'] = players[player_id]
    elif stats_by == 'goalsByGameSituation':
        values = _goals_by_situation(parsed)
        values['Player'] = players[player_id]
    elif stats_by == 'statsSingleSeason':
        values = _season_stats(parsed)
        values['Player'] = players[player_id]

    return values


def get_player_id(player_name, team_id, season):
    r = requests.get(f'https://statsapi.web.nhl.com/api/v1/teams/{team_id}?expand=team.roster&season={season}')
    parsed = json.loads(r.text)
    for player in parsed['teams'][0]['roster']['roster']:
        if player['person']['fullName'] == player_name:
            return player['person']['id']


def get_roster(team_id, season):
    r = requests.get(f'https://statsapi.web.nhl.com/api/v1/teams/{team_id}/roster?season={season}')
    parsed = json.loads(r.text)
    roster = []

    try:
        for player in parsed['roster']:
            roster.append({'ID': player['person']['id'], 'Player': player['person']['fullName']})
    except KeyError:
        pass

    return roster


def get_roster_list(team_id, season):
    r = requests.get(f'https://statsapi.web.nhl.com/api/v1/teams/{team_id}?expand=team.roster&season={season}')
    parsed = json.loads(r.text)
    roster_list = [player['person']['fullName'] for player in parsed['teams'][0]['roster']['roster']]
    return roster_list


def _home_and_away(parsed):
    home = parsed['stats'][0]['splits'][0]['stat']
    home['Season'] = parsed['stats'][0]['splits'][0]['season']
    home['Stat Type'] = 'Home'

    away = parsed['stats'][0]['splits'][1]['stat']
    away['Season'] = parsed['stats'][0]['splits'][1]['season']
    away['Stat Type'] = 'Away'

    return home, away


def _goals_by_situation(parsed):
    goals = parsed['stats'][0]['splits'][0]['stat']
    goals['Season'] = parsed['stats'][0]['splits'][0]['season']
    goals['Stat Type'] = 'Situation'

    return goals


def _season_stats(parsed):
    stats = parsed['stats'][0]['splits'][0]['stat']
    stats['Season'] = parsed['stats'][0]['splits'][0]['season']
    stats['Stat Type'] = 'Full Season'

    return stats


def get_game_stats(season, game_type, game_number):
    r = requests.get(f'https://statsapi.web.nhl.com/api/v1/game/{season}{game_type}{game_number}/feed/live')
    parsed = json.loads(r.text)
    try:
        all_plays = parsed['liveData']['plays']['allPlays']
    except KeyError:
        return []

    stats_list = []
    _game_type = {
        '01': 'Preseason',
        '02': 'Regular Season',
        '03': 'Playoffs',
        '04': 'All Star'
    }

    full_season = int(f'{season}{int(season) + 1}')
    shared_stats = {
        'Season': full_season,
        'Game Type': _game_type[game_type],
        'Game Number': int(game_number),
        'Home': parsed['gameData']['teams']['home']['name'],
        'Away': parsed['gameData']['teams']['away']['name'],
        'Game Time': parsed['gameData']['datetime']['dateTime'],
    }

    events_list = []
    for play in all_plays:
        try:
            players = play['players']
        except KeyError:
            continue
        for player in players:
            event_data = shared_stats.copy()
            event_data['Team'] = play['team']['name']
            event_data['Player'] = player['player']['fullName']
            event_data['Event'] = play['result']['event']
            event_data['Outcome'] = player['playerType']
            event_data['Period'] = play['about']['period']
            event_data['Period Time'] = play['about']['periodTime']
            try:
                event_data['Strength'] = play['result']['strength']['name']
                event_data['GWG'] = play['result']['gameWinningGoal']
                event_data['Empty Net'] = play['result']['emptyNet']
            except KeyError:
                pass
            try:
                event_data['x'] = play['coordinates']['x']
                event_data['y'] = play['coordinates']['y']
            except KeyError:
                pass
            events_list.append(event_data)
    stats_list.append(events_list)

    team_list = []
    player_list = []
    for team in parsed['liveData']['boxscore']['teams']:
        team_data = shared_stats.copy()
        team_data['Team'] = parsed['liveData']['boxscore']['teams'][team]['team']['name']
        team_stats = parsed['liveData']['boxscore']['teams'][team]['teamStats']['teamSkaterStats']
        team_data.update(team_stats)
        team_list.append(team_data)

        for skater in parsed['liveData']['boxscore']['teams'][team]['players']:
            try:
                player_data = shared_stats.copy()
                player_data['Team'] = parsed['liveData']['boxscore']['teams'][team]['team']['name']
                player_data['Player'] = parsed['liveData']['boxscore']['teams'][team]['players'][skater]['person'][
                    'fullName']
                player_data.update(
                    parsed['liveData']['boxscore']['teams'][team]['players'][skater]['stats']['skaterStats'])
                player_list.append(player_data)
            except KeyError:
                pass
    stats_list.append(team_list)
    stats_list.append(player_list)
    return stats_list


def get_all_players(season):
    players = {}
    for team_id in v.recent_teams_by_id:
        players.update(get_roster(team_id, season))

    return players


def get_shift_data(season, game_type, game_number):
    r = requests.get(
        f'https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={season}{game_type}{game_number}')
    parsed = json.loads(r.text)
    try:
        all_shifts = parsed['data']
    except KeyError:
        return []

    shift_list = []
    _game_type = {
        '01': 'Preseason',
        '02': 'Regular Season',
        '03': 'Playoffs',
        '04': 'All Star'
    }

    full_season = int(f'{season}{int(season) + 1}')
    shared_stats = {
        'Season': full_season,
        'Game Type': _game_type[game_type],
        'Game Number': int(game_number),
    }

    for shift in all_shifts:
        shift_data = shared_stats.copy()
        shift_data['Player Name'] = f'{shift["firstName"]} {shift["lastName"]}'
        shift_data['Period'] = shift['period']
        shift_data['Shift Number'] = shift['shiftNumber']
        shift_data['Shift Start Time'] = shift['startTime']
        shift_data['Shift End Time'] = shift['endTime']
        shift_data['Shift Duration'] = shift['duration']
        shift_data['Team'] = shift['teamName']
        shift_list.append(shift_data)

    return shift_list
