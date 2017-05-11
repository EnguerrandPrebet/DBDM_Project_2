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

#

def diff_year(matches_perspective):
    matches_perspective['kills'] = matches_perspective['kills'].apply(literal_eval)
    matches_perspective['enemyKills'] = matches_perspective['enemyKills'].apply(literal_eval)
    
    num_kills(matches_perspective)
    num_deaths(matches_perspective)
    print("total:\n",matches_perspective.describe())

    match_2016 = matches_perspective[matches_perspective['Year'] == 2016]
    match_2017 = matches_perspective[matches_perspective['Year'] == 2017]
    print("2016:\n",match_2016.describe())
    print("2017:\n",match_2017.describe())
    
def num_kills(df):
    df['num_kills'] = df['kills'].apply(lambda x: len(x))
    df['num_assist'] = df['kills'].apply(lambda x: sum([len(kill) - 3 for kill in x]))

def num_deaths(df): #Surtout pour verifier les valeurs obtenues avec kills
    df['num_death'] = df['enemyKills'].apply(lambda x: len(x))

"""Incomplet mais juste pour pas que j'ai a chercher
def unlist_kda(df,team=True,enemyTeam=True):
    if(not team and not enemyTeam):
        print("T'as rien compris gros !")
    
    if(team):
        pd.DataFrame({'a':np.repeat(df.a.values, df.b.str.len()),
                        'b':np.concatenate(df.b.values)})
"""

#

def diff_champ(matches_perspective):
    
    match_europe = matches_perspective[matches_perspective['League'] == 'Europe']
    match_na = matches_perspective[matches_perspective['League'] == 'North_America']
    match_korea = matches_perspective[matches_perspective['League'] == 'LCK']
    match_mid = matches_perspective[matches_perspective['League'] == 'Mid-Season_Invitational']
    match_WC = matches_perspective[matches_perspective['League'] == 'Season_World_Championship']
    
#

def fst_blood(matches_perspective):
    
    def func_alacon(x):
        if(len(x[0]) != 0):
            z = min(x,key = lambda y: y[0])
            return z[0]
        else:
            return 100
            
    matches_perspective['FK'] = matches_perspective['kills'].apply(func_alacon)
    matches_perspective['FKenemy'] = matches_perspective['enemyKills'].apply(func_alacon)
    
    matches_perspective['FB'] = (matches_perspective.FK < matches_perspective.FKenemy)
    
    matches_perspective2 = matches_perspective[(matches_perspective['FK'] != matches_perspective['FKenemy'])] #First blood at the same time, result unexpected 0.06 sec
    
    match_get_FB = matches_perspective2[matches_perspective2.FB]
    
    return match_get_FB #62.9% de winrate
    
#

def fst_objective(matches_perspective,str1,str2):
    
    def func_alacon(x):
        if(len(x) != 0):
            return min(x)
        else:
            return 100
    matches_perspective['you'] = matches_perspective[str1].apply(func_alacon)
    matches_perspective['notyou'] = matches_perspective[str2].apply(func_alacon)
    
    #matches_perspective = matches_perspective[(matches_perspective['FT'] != matches_perspective['FTenemy'])]
    
    matches_perspective['objective'] = (matches_perspective.you < matches_perspective.notyou)

    match_got_objective = matches_perspective[matches_perspective.objective]
    
    return match_got_objective
    
#

def imply_fst_obj(matches,str1,str2,str3,str4):
    #Compute data for first objective
    if(str1 == 'kills'):
        fst_blood(matches)
        matches = matches.rename(columns={'FB':'obj1','FK':'obj1a','FKenemy':'obj1e'})
    else:
        fst_objective(matches,str1,str2)
        matches = matches.rename(columns={'objective':'obj1','you':'obj1a','notyou':'obj1e'})
    
    #Compute data for second objective
    if(str3 == 'kills'):
        fst_blood(matches)
        matches = matches.rename(columns={'FB':'obj2','FK':'obj2a','FKenemy':'obj2e'})
    else:
        fst_objective(matches,str3,str4)
        matches = matches.rename(columns={'objective':'obj2','you':'obj2a','notyou':'obj2e'})
     
    #Comparison 
    result1 = matches[['result']][matches.obj1 & ~ matches.obj2].mean().tolist()[0]
    
    #Implication
    #Considering that both objectives are taken
    matches_both = matches[matches.obj1 & matches.obj2]
    #print(matches_both[['result']].count(),matches_both[['result']].mean())
    
    #If the first objective is done first
    result2 = ((matches_both[matches_both.obj1a < matches_both.obj2a][['result']].count()/matches_both[['result']].count()).tolist()[0])
    """#Or the second
    print(matches_both[matches_both.obj1a > matches_both.obj2a][['result']].count(),matches_both[matches_both.obj1a > matches_both.obj2a][['result']].mean())"""
    
    return result1,result2
    

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

    #freq_win_early_kills(matches_perspective)
    #diff_year(matches_perspective) #TODO
    #diff_champ(matches_perspective) #TODO
    
    paires = [('kills','enemyKills'),('towers','enemyTowers'),('heralds','enemyHeralds'),('dragons','enemyDragons'),('barons','enemyBarons'),('inhibs','enemyInhibs')]
    for paire in paires:
        matches_perspective[paire[0]] = matches_perspective[paire[0]].apply(literal_eval)
        matches_perspective[paire[1]] = matches_perspective[paire[1]].apply(literal_eval)
        
        if(paire[0] == 'kills'):
            print(paire[0],fst_blood(matches_perspective)[['result']].mean().tolist()[0])
        else:
            print(paire[0],fst_objective(matches_perspective,*paire)[['result']].mean().tolist()[0])
            
    #print(fst_objective(matches_perspective,'towers','enemyTowers')) #64.3%
    #print(fst_objective(matches_perspective,'heralds','enemyHeralds')) #66.5%
    #print(fst_objective(matches_perspective,'dragons','enemyDragons')) #63.9%
    #print(fst_objective(matches_perspective,'barons','enemyBarons')) #83.6%
    #print(fst_objective(matches_perspective,'inhibs','enemyInhibs')) #90,6%
    
    t,t2 = [],[]
    for paire_1 in paires:
        t.append([])
        t2.append([])
        for paire_2 in paires:
            if(paire_1 != paire_2):
                x = imply_fst_obj(matches_perspective,*paire_1,*paire_2)
                print(paire_1[0],paire_2[0],x)
                t[-1].append(int(x[0]*10000)/100.0)
                t2[-1].append(int(x[1]*10000)/100.0)
            else:
                t[-1].append('/////')
                t2[-1].append('/////')
                
    for i in range(len(t)):
        for j in range(len(t[i])):
            if(i != j):
                print(t[i][j] + t[j][i])
    print(np.matrix(t))
    print(np.matrix(t2))
    #print(imply_fst_obj(matches_perspective,'towers','enemyTowers','dragons','enemyDragons')
    #matches_perspective.to_csv('test.csv')

    """x = gold[gold.NameType == 'golddiff'].describe().drop['std', 'count', '25%', '50%', '75%', 'max']
    x.plot.hist()
    
    plt.show()"""

    #Reunir par matchs-ups.
    test_group = matches_perspective.groupby(by=['Team','enemyTeam'])
    #print(test_group.size().describe()) #7 games en moyenne, mediane a 5
