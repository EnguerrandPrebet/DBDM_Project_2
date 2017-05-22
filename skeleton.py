import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ast import literal_eval
import functools
#import seaborn as sn

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
    plt.figure()
    plt.plot(abs, ord, '-o')
    plt.xlabel('Game time')
    plt.ylabel('Win rate')
    plt.legend(['Win rate vs game time when \nkills have been done at this time'],
               loc='upper right')
    plt.show()

#
  
def num_kills(df):
    df['num_kills'] = df['kills'].apply(lambda x: len(x))
    df['num_assist'] = df['kills'].apply(lambda x: sum([len(kill) - 3 for kill in x]))

def num_deaths(df): #Surtout pour verifier les valeurs obtenues avec kills
    df['num_death'] = df['enemyKills'].apply(lambda x: len(x))



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

    matches2 = matches_perspective[(matches_perspective['FK'] != matches_perspective['FKenemy'])] #First blood at the same time, result unexpected 0.06 sec
    
    match_get_FB = matches2[matches2.FB]

    return matches2, match_get_FB #62.9% de winrate
    
#

def fst_objective(matches_perspective,str1,str2):
    
    def func_alacon(x):
        if(len(x) != 0):
            return min(x)
        else:
            return 100
    matches_perspective['you'] = matches_perspective[str1].apply(func_alacon)
    matches_perspective['notyou'] = matches_perspective[str2].apply(func_alacon)
    
    matches_perspective = matches_perspective[(matches_perspective['you'] != matches_perspective['notyou'])]
    
    matches_perspective['objective'] = (matches_perspective.you < matches_perspective.notyou)

    match_got_objective = matches_perspective[matches_perspective.objective]
    
    return matches_perspective, match_got_objective
    
#

def imply_fst_obj(matches,str1,str2,str3,str4):
    #Compute data for first objective
    if(str1 == 'kills'):
        matches = fst_blood(matches)[0]
        matches = matches.rename(columns={'FB':'obj1','FK':'obj1a','FKenemy':'obj1e'})
    else:
        matches = fst_objective(matches,str1,str2)[0]
        matches = matches.rename(columns={'objective':'obj1','you':'obj1a','notyou':'obj1e'})
    
    #Compute data for second objective
    if(str3 == 'kills'):
        matches = fst_blood(matches)[0]
        matches = matches.rename(columns={'FB':'obj2','FK':'obj2a','FKenemy':'obj2e'})
    else:
        matches = fst_objective(matches,str3,str4)[0]
        matches = matches.rename(columns={'objective':'obj2','you':'obj2a','notyou':'obj2e'})
     
    #Comparison 
    result1 = matches[['result']][matches.obj1 & ~ matches.obj2].mean().tolist()[0]
    #Implication
    #Considering that both objectives are taken
    matches_both = matches[matches.obj1 & matches.obj2]
    #print(matches_both[['result']].count(),matches_both[['result']].mean())
    
    #If the first objective is done first
    result2 = ((matches_both[matches_both.obj1a < matches_both.obj2a][['result']].count()/matches_both[['result']].count()).tolist()[0])
    
    return result1,result2
    

def plot_obj_winrate(matches_perspective,paires):
	
	df = pd.DataFrame()
	
	for paire in paires:
        if(paire[0] == 'kills'):
            df['fb'] = fst_blood(matches_perspective)[1]['result']
        else:
            df[paire[0]] = fst_objective(matches_perspective,*paire)[1]['result']
    
    plt.figure()
    df.mean().apply(lambda x: x * 100).plot(kind='bar')
    plt.show()

## Predictions sur 5 minutes

def fst_blood_2(matches):#Extraire les first blood qui a fait le first blood à moins de 10 minutes et s'il a été fait avant 5 minutes
    
    def func_alacon(x):
        if(len(x[0]) != 0):
            z = min(x,key = lambda y: y[0])
            return z[0]
        else:
            return 100
            
    matches['FK'] = matches['kills'].apply(func_alacon)
    matches['FKenemy'] = matches['enemyKills'].apply(func_alacon)
    
    matches['FB'] = matches.apply(lambda x: ((x.FK < 10) & (x.FK < x.FKenemy)) - ((x.FKenemy < 10) & (x.FKenemy < x.FK)), axis = 1)
    
    matches['FB_early'] = ((matches.FK < 5) | (matches.FKenemy < 5))
     
    matches2 = matches[(matches['FK'] != matches['FKenemy'])] #First blood at the same time, result unexpected 0.06 sec
    
    return matches2

def gold_diff_extract(matches,gold):#Extraction de la différence de gold à 10 minutes, et distinction sur l'écart de 400 gold
    gold_10min = gold['min_10'][(gold['NameType'] == 'goldblue') |(gold['NameType'] == 'goldred')]
    print(gold_10min.describe())
    
    gold_400 = gold['min_10'][gold['NameType'] == 'golddiff'].apply(abs)
    gold_400 = gold_400[gold_400 > 400]
    print(gold_400.describe())
    
    gold = gold[['MatchHistory','min_10']][gold['NameType'] == 'golddiff']
    gold['GD'] = gold['min_10'].apply(lambda x: (x > 400) - (x < -400) + (x > 900) - (x < -900))
    fusion = pd.merge(matches,gold,how='left',on='MatchHistory')
    fusion['GD'] = fusion.apply(lambda x: (1 - 2*(x.side == 'red')) * x.GD, axis = 1)
    
    return fusion
    
def predictions(matches,gold): #Prédictions à partir des extractions
    matches = fst_blood_2(matches)
    
    fusion = gold_diff_extract(matches,gold)
    
    predict1 = fusion.groupby(['FB','FB_early','GD'])
    print(predict1['result'].describe())
    predict2 = fusion.groupby(['FB','GD'])
    print(predict2['result'].describe())
    
    predict3 = fusion.groupby(['GD'])
    print(predict3['result'].describe())


def init():
    main_file = pd.read_csv('_LeagueofLegends.csv')
    #match_players = pd.read_csv('LeagueofLegends.csv')
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
    
	return matches_perspective, gold

def eval_list(matches, paires):
    for paire in paires:
        matches_perspective[paire[0]] = matches_perspective[paire[0]].apply(literal_eval)
        matches_perspective[paire[1]] = matches_perspective[paire[1]].apply(literal_eval)
        

	
    
def implications(matches, paires):

    t,t2 = [[0 for j in range(len(paires))] for i in range(len(paires))], [[0 for j in range(len(paires))] for i in range(len(paires))]
    for (i,paire_1) in enumerate(paires):
        for (j,paire_2) in enumerate(paires):
            if(i != j):
                x = imply_fst_obj(matches_perspective,*paire_1,*paire_2)
                t[i][j] = int(x[0]*10000)/100.0
                t2[i][j] = int(x[1]*10000)/100.0
            else:
                t[i][j] = '\ '
                t2[i][j] = '\ '
    fig,ax = plt.subplots()
	table = ax.table(cellText=t, cellLoc='center', rowLabels=[x[0] for x in paires], colLabels=[x[0] for x in paires], loc='center')
    ax.axis('tight')
    ax.axis('off')
	ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    
    fig.show()
    
    fig2,ax2 = plt.subplots()
	table2 = ax2.table(cellText=t2, cellLoc='center', rowLabels=[x[0] for x in paires], colLabels=[x[0] for x in paires], loc='center')
    ax2.axis('tight')
    ax2.axis('off')
	ax2.xaxis.set_visible(False)
    ax2.yaxis.set_visible(False)

	fig2.show()
	
if __name__ == '__main__':    
	
	matches_perspective, gold = init()
	
    freq_win_early_kills(matches_perspective)
    
	paires = [('kills','enemyKills'),('towers','enemyTowers'),('heralds','enemyHeralds'),('dragons','enemyDragons'),('barons','enemyBarons'),('inhibs','enemyInhibs')]
	
	eval_list(matches_perspective,paires)
	
	plot_obj_winrate(matches_perspective,paires)
	
    predictions(matches_perspective,gold)
	
	implications(matches_perspective,paires)
	

	
    #matches_perspective.to_csv('test.csv')

    
    """x = gold[gold.NameType == 'golddiff'].describe().drop['std', 'count', '25%', '50%', '75%', 'max']
    x.plot.hist()
    
    plt.show()"""

    #Reunir par matchs-ups.
    test_group = matches_perspective.groupby(by=['Team','enemyTeam'])
    #print(test_group.size().describe()) #7 games en moyenne, mediane a 5
