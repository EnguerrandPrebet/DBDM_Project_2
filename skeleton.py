import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ast import literal_eval
import functools

def early_kill(minute, c):
    return str(list(filter(lambda x: len(x) > 0 and int(x[0]) < minute, literal_eval(c))))

def win_kill_early(minute, matches):
    win_early_kills = matches_perspective[['result', 'kills']]

    early_kills = win_early_kills['kills']\
        .apply(functools.partial(early_kill, minute))

    win_early_kills['kills'] = early_kills

    win_early_kills = win_early_kills[win_early_kills['kills'] != '[]']

    win_early_kills.describe().to_csv('win_early.csv')

    return win_early_kills['result'].mean()


def freq_win_early_kills(matches):
    df = pd.DataFrame()
    for minute in range(1, 6):
        df[minute] = [win_kill_early(minute, matches)]

    abs, ord = list(df), df.iloc[[0]].values.tolist()[0]

    #plt.scatter(x=abs, y=ord)
    plt.plot(abs, ord, '-o')
    plt.xlabel('Game time')
    plt.ylabel('Win rate')
    plt.legend(['Win rate vs game time when \nkills have been done at this time'],
               loc='upper right')
    plt.show()


if __name__ == '__main__':

    main_file = pd.read_csv('_LeagueofLegends.csv')
    match_players = pd.read_csv('LeagueofLegends.csv')
    gold = pd.read_csv('goldValues.csv')

    matches = main_file[((main_file['Year'] == 2017) | (main_file['Year'] == 2016))
                        & ((main_file['League'] == 'Europe') |
                        (main_file['League'] == 'North_America') |
                        (main_file['League'] == 'LCK') |
                        (main_file['League'] == 'Season_World_Championship') |
                        (main_file['League'] == 'Mid-Season_Invitational')
                        )].drop(['blueTop', 'blueTopChamp', 'goldblueTop', 'blueJungle', 'blueJungleChamp', 'goldblueJungle',
                  'blueMiddle', 'blueMiddleChamp', 'goldblueMiddle', 'blueADC', 'blueADCChamp',
                  'goldblueADC', 'blueSupport', 'blueSupportChamp', 'goldblueSupport',
                  'redTop', 'redTopChamp', 'goldredTop', 'redJungle', 'redJungleChamp', 'goldredJungle',
                  'redMiddle', 'redMiddleChamp', 'goldredMiddle', 'redADC', 'redADCChamp',
                  'goldredADC', 'redSupport', 'redSupportChamp', 'goldredSupport'
                  ], axis=1)

    matches_red = matches.drop(['bResult'], axis=1)\
        .rename(columns={'blueTeamTag':'enemyTeam', 'rResult':'result',
                         'redTeamTag':'Team',
                         'goldblue':'enemyGold',
                         'bKills':'enemyKills', 'bTowers':'enemyTowers',
                         'bInhibs':'enemyInhibs', 'bDragons':'enemyDragons',
                         'bBarons':'enemyBarons', 'bHeralds':'enemyHeralds',
                         'goldred': 'gold',
                         'rKills': 'kills', 'rTowers': 'towers',
                         'rInhibs': 'inhibs', 'rDragons': 'dragons',
                         'rBarons': 'barons', 'rHeralds': 'heralds',
                         'redBans':'bans', 'blueBans':'enemyBans'
                         })
    matches_red['side'] = 'red'

    matches_red = matches_red.sort_index()

    matches_blue = matches.drop(['rResult'], axis=1)\
        .rename(columns={'redTeamTag':'enemyTeam', 'bResult':'result',
                         'blueTeamTag':'Team',
                         'goldred':'enemyGold',
                         'rKills':'enemyKills', 'rTowers':'enemyTowers',
                         'rInhibs':'enemyInhibs', 'rDragons':'enemyDragons',
                         'rBarons':'enemyBarons', 'rHeralds':'enemyHeralds',
                         'goldblue': 'gold',
                         'bKills': 'kills', 'bTowers': 'towers',
                         'bInhibs': 'inhibs', 'bDragons': 'dragons',
                         'bBarons': 'barons', 'bHeralds': 'heralds',
                         'redBans':'bans', 'blueBans':'enemyBans'
                         })
    matches_blue['side'] = 'blue'

    matches_blue = matches_blue.sort_index()

    matches_perspective = pd.concat([matches_red, matches_blue])

    freq_win_early_kills(matches_perspective)

    #matches_perspective.to_csv('test.csv')

    """x = gold[gold.NameType == 'golddiff'].describe().drop['std', 'count', '25%', '50%', '75%', 'max']
    x.plot.hist()
    
    plt.show()"""