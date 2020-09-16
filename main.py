"""
Module used for writing large amounts of api data to different xlsx spreadsheets for personal use.

Contains functions used to get data for:
    write_season_team_stats - get all team data for given seasons.
    write_season_player_stats - get all season stats for all players.
    write_game_stats - gets all game specific data for all games in given seasons.
    write_player_ids - gets the full rosters from every team for all seasons given.
    write_shift_data - gets the shift information from every game for given seasons.

NOTE:
    Various functions in this project currently require an NHL_players.xlsx spreadsheet that
    contains player names and ids to be present within this project directory.
    If this file is missing, it can be recreated with write_player_ids.

    Shift data does not appear to be collected prior to 2010.
    Trying to get data before 2010 will result in an empty dataframe
"""

import os
import time

import pandas as pd
import requests

import api_parse as api
import utils
import values as v

ROOT = os.getcwd() + '/csv_data/'
START_SEASON = 2005
END_SEASON = 2019
MAX_GAMES = 1271


def _game_stats(season):
    """
    Scrape the api and return lists of dicts containing game level data.
    Gets the game data for every game in the season for regular season and playoffs.
    Returns lists of all event data, team data, and player data.

    Usage:
        events_data, team_data, player_data = _game_stats(20152016)

    :param season: Season to scrape data for.
    :type season: str
    :return: List of dicts for event data per game, team stats per game, and player data per game
    :rtype: (list of dict, list of dict, list of dict)
    """
    # TODO add logic for passing playoff game numbers to collect playoff data
    game_types = ['02']
    event_data = []
    team_data = []
    player_data = []

    for game_type in game_types:
        for game in range(1, MAX_GAMES + 1):
            # request for game needs to be in format 0001
            game_number = str(game).zfill(4)
            print(f'{game_type} - {game_number}')
            stats = api.get_game_stats(season, game_type, game_number)
            if stats:
                event_data.extend(stats[0])
                team_data.extend(stats[1])
                player_data.extend(stats[2])
                time.sleep(1)
            else:
                break

    return event_data, team_data, player_data


def _season_team_stats(season):
    """
    Scrape the api and return lists of dicts containing season stats for each team.
    Returns lists of all team stats for raw values and season ranks (1st, 3rd, etc.).

    Usage:
        stats, ranks = _season_team_stats(20152016)

    :param season: Season to scrape data for.
    :type season: str
    :return: List of dicts for all team stats and all team stat ranks
    :rtype: (list of dict, list of dict)
    """
    stats_list = []
    ranks_list = []
    # dynamically find teams by season instead?
    # not sure if api lists teams per season - wasting time on api calls
    for team_id in v.all_teams_by_id:
        try:
            stats, ranks = api.get_team_stats(team_id, season=season)
            time.sleep(1)
            stats['Team'] = v.all_teams_by_id[team_id]
            stats_list.append(stats)

            ranks_list.append(ranks)
            ranks['Team'] = v.all_teams_by_id[team_id]
        except KeyError:
            pass

    return stats_list, ranks_list


def _season_player_stats(season):
    """
    Scrape the api and return lists of dicts containing season stats for each player.
    Collects player stats for:
        Full Season, Home, Away, Situation

    Usage:
        stats = _season_player_stats(20152016)

    :param season: Season to scrape data for.
    :type season: str
    :return: List of dicts for all player stats.
    :rtype: list of dict
    """
    # get all players for season so don't have to load from xlsx?
    # Slower and lots of requests but don't need xlsx dependency
    players = utils.players_by_id(os.getcwd() + '/NHL_players.xlsx')
    # different categories of stats for each player
    stats_by = [
        'homeAndAway',
        'goalsByGameSituation',
        'statsSingleSeason',
    ]
    stats_list = []

    def _get_stats(_player_id, _by, _season):
        try:
            stats = api.get_player_stats(_player_id, _by, _season)
            if by == 'homeAndAway':
                stats_list.append(stats[0])
                stats_list.append(stats[1])
            else:
                stats_list.append(stats)
        except (KeyError, IndexError):
            pass

    for player_id in players:
        print(player_id)
        for by in stats_by:
            # makes LOTS of requests for every player, for different situations, for every season
            # while loop to to make requests until getting kicked out
            # pause for the timeout then try to resume
            while True:
                try:
                    _get_stats(player_id, by, season)
                    break
                except requests.exceptions.ConnectionError:
                    print('sleeping')
                    time.sleep(1800)

    return stats_list


def _shift_data(season):
    """
    Scrape the api and return lists of dicts containing shift details for each player.

    Usage:
        shifts = _shift_data(20152016)

    :param season: Season to scrape data for.
    :type season: str
    :return: List of dicts for all shift information for every player.
    :rtype: list of dict
    """
    game_types = ['02']
    shifts = []

    def _get_stats(_season, _game_type, _game):
        game_number = str(_game).zfill(4)
        print(f'{_game_type} - {game_number}')
        stats = api.get_shift_data(_season, _game_type, game_number)
        if stats:
            shifts.extend(stats)
            time.sleep(1)

    for game_type in game_types:
        for game in range(1, MAX_GAMES + 1):
            while True:
                try:
                    _get_stats(season, game_type, game)
                    break
                except requests.exceptions.ConnectionError:
                    print('sleeping')
                    time.sleep(1800)

    return shifts


def write_season_team_stats(filename, start_season, end_season=None):
    """
    Function used to write all team stats for every specified season to provided xlsx file.
    Can optionally provide a single season or a start and end season if wanting to scrape a range of seasons.
    If the provided filename already exists, will append new data to file.
    Output xlsx will write data to individual 'Stats' and 'Ranks' tabs.

    :param filename: Complete filepath to write data to.
    :type filename: str
    :param start_season: Start season to get data from.
    :type start_season: int or str
    :param end_season: Final season to get data from (inclusive).
    :type end_season: int or str
    """
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    # format seasons to be api-friendly
    if end_season is not None:
        seasons = utils.get_season_list(start_season, end_season)
    else:
        seasons = utils.get_season_list(start_season, start_season)

    stats_list = []
    ranks_list = []

    try:
        for season in seasons:
            print(season)
            stats, ranks = _season_team_stats(season)
            stats_list.extend(stats)
            ranks_list.extend(ranks)
    # make sure to write whatever function has managed to scrape in event of error
    finally:
        # create dataframes, rename cols from api json format to 'prettier' format, and change col order
        df_stats = pd.DataFrame(stats_list)
        df_stats = utils.rename_cols(df_stats)
        df_stats = utils.update_cols(df_stats, ['Season', 'Team'])

        df_ranks = pd.DataFrame(ranks_list)
        df_ranks = utils.rename_cols(df_ranks)
        df_ranks = utils.update_cols(df_ranks, ['Season', 'Team'])

        if os.path.exists(filename):
            # load previous dataframe and append newest data
            og_stats = pd.read_excel(filename, sheet_name='Stats')
            df_stats = og_stats.append(df_stats, ignore_index=True).drop_duplicates()

            og_ranks = pd.read_excel(filename, sheet_name='Ranks')
            df_ranks = og_ranks.append(df_ranks, ignore_index=True).drop_duplicates()

        df_stats.to_excel(writer, index=False, sheet_name='Stats')
        df_ranks.to_excel(writer, index=False, sheet_name='Ranks')
        writer.close()


def write_season_player_stats(filename, start_season, end_season=None):
    """
    Function used to write all player stats for every specified season to provided xlsx file.
    Can optionally provide a single season or a start and end season if wanting to scrape a range of seasons.
    If the provided filename already exists, will append new data to file.
    Output xlsx will write data to a 'Player Stats' tab.

    :param filename: Complete filepath to write data to.
    :type filename: str
    :param start_season: Start season to get data from.
    :type start_season: int or str
    :param end_season: Final season to get data from (inclusive).
    :type end_season: int or str
    """
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    # format seasons to be api-friendly
    if end_season is not None:
        seasons = utils.get_season_list(start_season, end_season)
    else:
        seasons = utils.get_season_list(start_season, start_season)

    stats_list = []
    try:
        for season in seasons:
            print(season)
            stats = _season_player_stats(season)
            stats_list.extend(stats)
    # make sure to write whatever function has managed to scrape in event of error
    finally:
        # create dataframes, rename cols from api json format to 'prettier' format, and change col order
        stats_df = pd.DataFrame(stats_list)
        stats_df = utils.rename_cols(stats_df)
        stats_df = utils.update_cols(stats_df, ['Season', 'Player', 'Stat Type'])

        if os.path.exists(filename):
            # load previous dataframe and append newest data
            og_stats = pd.read_excel(filename)
            og_stats = utils.rename_cols(og_stats)
            stats_df = og_stats.append(stats_df, ignore_index=True).drop_duplicates()
        stats_df.to_excel(writer, index=False, sheet_name='Player Stats')

        writer.close()


def write_game_stats(filename, start_season, end_season=None):
    """
    Function used to write all game specific stats for every specified season to provided xlsx file.
    Can optionally provide a single season or a start and end season if wanting to scrape a range of seasons.
    If the provided filename already exists, will append new data to file.
    Output xlsx will write data to individual 'Events', 'Teams', and 'Players' tabs.

    :param filename: Complete filepath to write data to.
    :type filename: str
    :param start_season: Start season to get data from.
    :type start_season: int or str
    :param end_season: Final season to get data from (inclusive).
    :type end_season: int or str
    """
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    # format seasons to be api-friendly
    if end_season is not None:
        seasons = utils.get_season_list(start_season, end_season)
    else:
        seasons = utils.get_season_list(start_season, start_season)

    events_data = []
    team_data = []
    player_data = []
    try:
        for season in seasons:
            season = season[:4]
            print(season)
            events, team, player = _game_stats(season)
            events_data.extend(events)
            team_data.extend(team)
            player_data.extend(player)
    # make sure to write whatever function has managed to scrape in event of error
    finally:
        # create dataframes, rename cols from api json format to 'prettier' format, and change col order
        event_df = pd.DataFrame(events_data)
        event_df = utils.rename_cols(event_df)
        event_df = utils.update_cols(event_df, ['Season', 'Game Type', 'Game Number', 'Player', 'Team'])

        team_df = pd.DataFrame(team_data)
        team_df = utils.rename_cols(team_df)
        team_df = utils.update_cols(team_df, ['Season', 'Game Type', 'Game Number', 'Team'])

        player_df = pd.DataFrame(player_data)
        player_df = utils.rename_cols(player_df)
        player_df = utils.update_cols(player_df, ['Season', 'Game Type', 'Game Number', 'Player', 'Team'])

        if os.path.exists(filename):
            # load previous dataframe and append newest data
            og_data = pd.read_excel(filename, sheet_name=None)
            event_df = og_data['Events'].append(event_df, ignore_index=True).drop_duplicates()
            team_df = og_data['Teams'].append(team_df, ignore_index=True).drop_duplicates()
            player_df = og_data['Players'].append(player_df, ignore_index=True).drop_duplicates()

        event_df.to_excel(writer, index=False, sheet_name='Events')
        team_df.to_excel(writer, index=False, sheet_name='Teams')
        player_df.to_excel(writer, index=False, sheet_name='Players')

        writer.close()


def write_player_ids(filename, start_season, end_season=None):
    """
    Function used to write all player names and ids for every specified season to provided xlsx file.
    Can optionally provide a single season or a start and end season if wanting to scrape a range of seasons.
    If the provided filename already exists, will append new data to file.
    Output xlsx will write data to a 'Players' tab.

    :param filename: Complete filepath to write data to.
    :type filename: str
    :param start_season: Start season to get data from.
    :type start_season: int or str
    :param end_season: Final season to get data from (inclusive).
    :type end_season: int or str
    """
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    # format seasons to be api-friendly
    if end_season is not None:
        seasons = utils.get_season_list(start_season, end_season)
    else:
        seasons = utils.get_season_list(start_season, start_season)

    player_data = []
    try:
        for season in seasons:
            print(season)
            for team in v.all_teams_by_id:
                roster = api.get_roster(team, season)
                player_data.extend(roster)
                time.sleep(1)
    # make sure to write whatever function has managed to scrape in event of error
    finally:
        # create dataframes, rename cols from api json format to 'prettier' format, and change col order
        player_df = pd.DataFrame(player_data).drop_duplicates()
        player_df = utils.rename_cols(player_df)

        if os.path.exists(filename):
            # load previous dataframe and append newest data
            og_data = pd.read_excel(filename)
            player_df = og_data.append(player_df, ignore_index=True).drop_duplicates()

        player_df.to_excel(writer, index=False, sheet_name='Players')

        writer.close()


def write_shift_data(filename, start_season, end_season=None):
    """
    Function used to write all shift information for every game and for every specified season to provided xlsx file.
    Can optionally provide a single season or a start and end season if wanting to scrape a range of seasons.
    If the provided filename already exists, will append new data to file.
    Output xlsx will write data to a 'Players' tab.

    :param filename: Complete filepath to write data to.
    :type filename: str
    :param start_season: Start season to get data from.
    :type start_season: int or str
    :param end_season: Final season to get data from (inclusive).
    :type end_season: int or str
    """
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    # format seasons to be api-friendly
    if end_season is not None:
        seasons = utils.get_season_list(start_season, end_season)
    else:
        seasons = utils.get_season_list(start_season, start_season)

    shift_data = []
    try:
        for season in seasons:
            season = season[:4]
            print(season)
            shifts = _shift_data(season)
            shift_data.extend(shifts)
            time.sleep(1)
    # make sure to write whatever function has managed to scrape in event of error
    finally:
        # create dataframes, rename cols from api json format to 'prettier' format, and change col order
        shift_df = pd.DataFrame(shift_data).drop_duplicates()
        shift_df = utils.rename_cols(shift_df)

        if os.path.exists(filename):
            # load previous dataframe and append newest data
            og_data = pd.read_excel(filename)
            shift_df = og_data.append(shift_df, ignore_index=True).drop_duplicates()

        shift_df.to_excel(writer, index=False, sheet_name='Players')

        writer.close()


if __name__ == '__main__':
    # team_stats_file = ROOT + '/NHL_team_stats.xlsx'
    # write_season_team_stats(team_stats_file, 1995, 2019)

    shift_file = ROOT + '/NHL_shift_data.xlsx'
    # shift data doesn't appear to be collected prior to 2010
    write_shift_data(shift_file, 2010, 2019)

    # player_stats_file = ROOT + '/NHL_player_stats.xlsx'
    # write_season_player_stats(player_stats_file, 2001, 2019)

    # game_stats_file = ROOT + '/NHL_game_stats.xlsx'
    # write_game_stats(game_stats_file, 1995, 2003)

    # roster_file = ROOT + '/NHL_players.xlsx'
    # write_player_ids(roster_file, 1995, 2019)
