def convert_season(season):
    return int(f'{season}{season+1}')


def get_season_list(start, stop):
    if len(str(start)) == 8 and len(str(stop)) == 8:
        start = start[:4]
        stop = stop[:4]
    return [f'{i}{i + 1}' for i in range(int(start), int(stop) + 1)]


def update_cols(df, first_order):
    cols = df.columns.values.tolist()
    for col in first_order:
        try:
            cols.remove(col)
        except ValueError:
            pass
    cols = first_order + cols
    df = df[cols]
    return df


def rename_cols(df):
    rename = {
        'gamesPlayed': 'Games Played',
        'wins': 'Wins',
        'losses': 'Losses',
        'ot': 'OTL',
        'pts': 'Points',
        'ptPctg': 'Points %',
        'goalsPerGame': 'Goals Per Game',
        'goalsAgainstPerGame': 'GA Per Game',
        'evGGARatio': 'EV GA Ratio',
        'powerPlayPercentage': 'Powerplay %',
        'powerPlayGoals': 'Powerplay Goals',
        'powerPlayAssists': 'Powerplay Assists',
        'powerPlayGoalsAgainst': 'Powerplay GA',
        'powerPlayOpportunities': 'Powerplays',
        'penaltyKillPercentage': 'PK %',
        'shotsPerGame': 'Shots Per Game',
        'shotsAllowed': 'Shots Allowed',
        'winScoreFirst': 'Win % Score First',
        'winOppScoreFirst': 'Win % Opp Score First',
        'winLeadFirstPer': 'Win % Lead First',
        'winLeadSecondPer': 'Win % Lead Second',
        'winOutshootOpp': 'Win % Outshoot Opp',
        'winOutshotByOpp': 'Win % Outshot By Opp',
        'faceOffsTaken': 'Faceoffs',
        'faceOffsWon': 'Faceoffs Won',
        'faceOffsLost': 'Faceoffs Lost',
        'faceOffWinPercentage': 'Faceoff Win %',
        'shootingPctg': 'Shooting %',
        'savePctg': 'Save %',
        'timeOnIce': 'TOI',
        'assists': 'Assists',
        'goals': 'Goals',
        'pim': 'PIM',
        'shots': 'Shots',
        'games': 'Games',
        'hits': 'Hits',
        'powerPlayPoints': 'Powerplay Points',
        'powerPlayTimeOnIce': 'Powerplay TOI',
        'evenTimeOnIce': 'Even Strength TOI',
        'penaltyMinutes': 'PIMs',
        'faceOffPct': 'Faceoff %',
        'shotPct': 'Shot %',
        'gameWinningGoals': 'GWG',
        'overTimeGoals': 'OT Goals',
        'shortHandedGoals': 'Shorthanded Goals',
        'shortHandedAssists': 'Shorthanded Assists',
        'shortHandedPoints': 'Shorthanded Points',
        'shortHandedTimeOnIce': 'SH TOI',
        'blocked': 'Blocked Shots',
        'plusMinus': 'Plus Minus',
        'points': 'Points',
        'shifts': 'Shifts',
        'timeOnIcePerGame': 'TOI per Game',
        'evenTimeOnIcePerGame': 'ES TOI per Game',
        'shortHandedTimeOnIcePerGame': 'SH TOI per Game',
        'powerPlayTimeOnIcePerGame': 'Powerplay TOI per Game',
        'fullName': 'Player Name',
        'takeaways': 'Takeaways',
        'giveaways': 'Giveaways',
        'link': 'API Link',
        'shootsCatches': 'Shoots (R/L)',
        'jerseyNumber': 'Jersey Number',
        'faceOffWins': 'Faceoff Win',
        'faceOffTaken': 'Faceoff Taken',
        'name': 'Position',
        'firstName': 'First Name',
        'lastName': 'Last Name',
        'primaryNumber': 'Number',
        'birthDate': 'Birth Date',
        'currentAge': 'Age',
        'birthCity': 'Birth City',
        'birthStateProvince': 'Birth State/Province',
        'birthCountry': 'Birth Country',
        'nationality': 'Nationality',
        'height': 'Height',
        'weight': 'Weight',
        'active': 'Currently Active',
        'alternateCaptain': 'Alternate Captain',
        'captain': 'Captain',
        'rookie': 'Rookie',
        'shutouts': 'Shutouts',
        'ties': 'Ties',
        'saves': 'Saves',
        'goalsInFirstPeriod': 'First Period Goals',
        'goalsInSecondPeriod': 'Second Period Goals',
        'goalsInThirdPeriod': 'Third Period Goals',
        'goalsInOvertime': 'Overtime Goals',
        'goalsTrailingByOne': 'Goals Trailing by One',
        'goalsTrailingByTwo': 'Goals Trailing by Two',
        'goalsTrailingByThreePlus': 'Goals Trailing by Three +',
        'goalsLeadingByOne': 'Goals Leading by One',
        'goalsLeadingByTwo': 'Goals Leading by Two',
        'goalsLeadingByThreePlus': 'Goals Leading by Three +',
        'goalsWhenTied': 'Goals When Tied',
        'powerPlaySaves': 'Power Play Saves',
        'shortHandedSaves': 'Short Handed Saves',
        'evenSaves': 'Even Saves',
        'powerPlayShots': 'Power Play Shots',
        'shortHandedShots': 'Short Handed Shots',
        'evenShots': 'Even Shots',
        'savePercentage': 'Save %',
        'goalAgainstAverage': 'GAA',
        'gamesStarted': 'Games Started',
        'shotsAgainst': 'Shots Against',
        'goalsAgainst': 'Goals Against',
        'powerPlaySavePercentage': 'PP Save %',
        'evenStrengthSavePercentage': 'ES Save %',
        'shortHandedSavePercentage': 'SH Save %',
    }

    df = df.rename(columns=rename)
    return df
