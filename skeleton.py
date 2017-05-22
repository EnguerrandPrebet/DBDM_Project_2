import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ast import literal_eval
import functools
#import seaborn as sn

##Initialisation

def init():#Getting the DB
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

def eval_list(matches, paires):#Transform string into list
    for paire in paires:
        matches_perspective[paire[0]] = matches_perspective[paire[0]].apply(literal_eval)
        matches_perspective[paire[1]] = matches_perspective[paire[1]].apply(literal_eval)
        
## Winrate avec des kills en early

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

## Observations sur le premier kill et les objectifs

def fst_blood(matches_perspective):#Columns to detect the first blood
    
    def func_alacon(x):
        if(len(x[0]) != 0):
            z = min(x,key = lambda y: y[0])
            return z[0]
        else:
            return 100
            
    matches_perspective['FK'] = matches_perspective['kills'].apply(func_alacon)
    matches_perspective['FKenemy'] = matches_perspective['enemyKills'].apply(func_alacon)
    
    matches_perspective['FB'] = (matches_perspective.FK < matches_perspective.FKenemy)

    matches2 = matches_perspective[(matches_perspective['FK'] != matches_perspective['FKenemy'])] #Unexpected result: First blood at the same time (~0.06 sec) have occured. As the behaviour is unknown, we forget this case.
    
    match_get_FB = matches2[matches2.FB]

    return matches2, match_get_FB

def fst_objective(matches_perspective,str1,str2):#Columns to detect who got the objective first
    
    def func_alacon(x):
        if(len(x) != 0):
            return min(x)
        else:
            return 100
    matches_perspective['you'] = matches_perspective[str1].apply(func_alacon)
    matches_perspective['notyou'] = matches_perspective[str2].apply(func_alacon)
    
    matches_perspective = matches_perspective[(matches_perspective['you'] != matches_perspective['notyou'])] #Delete cases where noone does the objective
    
    matches_perspective['objective'] = (matches_perspective.you < matches_perspective.notyou)

    match_got_objective = matches_perspective[matches_perspective.objective]
    
    return matches_perspective, match_got_objective

def plot_obj_winrate(matches_perspective,paires): #Conclusion when looking at one objective
	
	df = pd.DataFrame()
	
	for paire in paires:
        if(paire[0] == 'kills'):
            df['fb'] = fst_blood(matches_perspective)[1]['result']
        else:
            df[paire[0]] = fst_objective(matches_perspective,*paire)[1]['result']
    
    plt.figure()
    df.mean().apply(lambda x: x * 100).plot(kind='bar')
    plt.show()
    
#

def imply_fst_obj(matches,str1,str2,str3,str4):#Comparing 2 objectives
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
     
    #Comparison (one but not the other)
    result1 = matches['result'][matches.obj1 & ~ matches.obj2].mean()
    
    #Implication (one imply the other)
    #Considering that the first objective is taken and noone got the second
    matches_both = matches[(matches.obj1) & (matches.obj1a < matches.obj2a) & (matches.obj1a < matches.obj2e)]
    #print(matches_both[['result']].count(),matches_both[['result']].mean())
    
    #Having the first will it help to get the second first
    if(matches_both['result'].count() == 0):
        result2 = -1
    else:
        result2 =(matches_both[(matches_both.obj2) & (matches_both.obj1a < matches_both.obj2a)]['result'].count() / matches_both['result'].count())
    
    return result1,result2, matches_both['result'].count()/matches['result'].count()
    
def implications(matches, paires):#Draw conclusions from the function above

    t,t2,t3 = [[0 for j in range(len(paires))] for i in range(len(paires))], [[0 for j in range(len(paires))] for i in range(len(paires))], [[0 for j in range(len(paires))] for i in range(len(paires))]
    for (i,paire_1) in enumerate(paires):
        for (j,paire_2) in enumerate(paires):
            if(i != j):
                x = imply_fst_obj(matches_perspective,*paire_1,*paire_2)
                t[i][j] = int(x[0]*10000)/100.0
                t2[i][j] = int(x[1]*10000)/100.0
                t3[i][j] = int(x[2]*10000)/100.0
                if(t[i][j] < 0):
                    t[i][j] = 'X'
                if(t2[i][j] < 0):
                    t2[i][j] = 'X'
                
            else:
                t[i][j] = '\ '
                t2[i][j] = '\ '
                t3[i][j] = '\ '
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
	
    fig3,ax3 = plt.subplots()
	table3 = ax3.table(cellText=t3, cellLoc='center', rowLabels=[x[0] for x in paires], colLabels=[x[0] for x in paires], loc='center')
	ax3.axis('tight')
    ax3.axis('off')
	ax3.xaxis.set_visible(False)
    ax3.yaxis.set_visible(False)

	fig3.show()


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

    #Gold à 10 minutes (outil de comparaison avec la valeur 400)
    gold_10min = gold['min_10'][(gold['NameType'] == 'goldblue') |(gold['NameType'] == 'goldred')]
    
    """plt.figure()
    gold_10min.plot.box()
    plt.show()"""
    
    
    #Répartition de ce que signifie (> 400)
    gold_400 = gold['min_10'][gold['NameType'] == 'golddiff'].apply(abs)
    gold_400 = gold_400[gold_400 > 400]
    
    """plt.figure()
    gold_400.plot.box()
    plt.show()
    print(gold_400.describe())"""
    
    gold = gold[['MatchHistory','min_10']][gold['NameType'] == 'golddiff']
    gold['GD'] = gold['min_10'].apply(lambda x: (x > 400) - (x < -400))
    fusion = pd.merge(matches,gold,how='left',on='MatchHistory')
    fusion['GD'] = fusion.apply(lambda x: (1 - 2*(x.side == 'red')) * x.GD, axis = 1)
    
    return fusion

def looking_at_gold(fusion):#Etude plus précise de l'intérêt de l'or
    x = [i*100 for i in range(0,30)]
    fusion['min_10'] = fusion.apply(lambda x: (1 - 2*(x['side'] == 'red')) * x['min_10'], axis = 1)
    y = [2*fusion[fusion['min_10'] > i*100]['result'].count()/fusion['result'].count() for i in range(0,30)]
    y2 = [fusion[fusion['min_10'] > i*100]['result'].mean() for i in range(0,30)]
    y3 = [fusion[(fusion['min_10'] > i*100) & (fusion['FB']==1)]['result'].mean() for i in range(0,30)]
    y4 = [fusion[(fusion['min_10'] > i*100) & (fusion['FB']==0)]['result'].mean() for i in range(0,30)]
    y5 = [fusion[(fusion['min_10'] > i*100) & (fusion['FB']==-1)]['result'].mean() for i in range(0,30)]
    plt.figure()
    plt.xlabel('Lower bound on gold differential after 10 minutes')
    plt.plot(x,y, label='Games')
    plt.plot(x,y2, label='Winrate')
    #plt.plot(x,y3, label='Winrate with FB')
    #plt.plot(x,y4, label='Winrate wo FB')
    #plt.plot(x,y5, label='Winrate when nothing happens')
    plt.legend()
    plt.show()
    
def predictions(matches,gold): #Prédictions à partir des extractions
    matches = fst_blood_2(matches)
    
    fusion = gold_diff_extract(matches,gold)
    
    predict1 = fusion.groupby(['FB','FB_early','GD'])
    #print(predict1['result'].describe()[['count','mean']])
    
    predict2 = fusion.groupby(['FB','GD'])
    #print(predict2['result'].describe()[['count','mean']])
    
    predict3 = fusion.groupby(['GD'])
    #print(predict3['result'].describe()[['count','mean']])

    looking_at_gold(fusion)

##Main

if __name__ == '__main__':    
	
	matches_perspective, gold = init()
	
    freq_win_early_kills(matches_perspective)
    
	paires = [('kills','enemyKills'),('towers','enemyTowers'),('heralds','enemyHeralds'),('dragons','enemyDragons'),('barons','enemyBarons'),('inhibs','enemyInhibs')]
	
	eval_list(matches_perspective,paires)
	
	plot_obj_winrate(matches_perspective,paires)
	
	implications(matches_perspective,paires)

    predictions(matches_perspective,gold)
	