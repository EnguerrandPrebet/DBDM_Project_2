import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

main_file = pd.read_csv('_LeagueofLegends.csv')
match_players = pd.read_csv('LeagueofLegends.csv')
gold = pd.read_csv('goldValues.csv')

matches = main_file[((main_file['Year'] == 2017) | (main_file['Year'] == 2016))
                    & ((main_file['League'] == 'Europe') |
                    (main_file['League'] == 'North_America') |
                    (main_file['League'] == 'LCK')
                    )].drop(['blueTop', 'blueTopChamp', 'goldblueTop', 'blueJungle', 'blueJungleChamp', 'goldblueJungle',
              'blueMiddle', 'blueMiddleChamp', 'goldblueMiddle', 'blueADC', 'blueADCChamp',
              'goldblueADC', 'blueSupport', 'blueSupportChamp', 'goldblueSupport',
              'redTop', 'redTopChamp', 'goldredTop', 'redJungle', 'redJungleChamp', 'goldredJungle',
              'redMiddle', 'redMiddleChamp', 'goldredMiddle', 'redADC', 'redADCChamp',
              'goldredADC', 'redSupport', 'redSupportChamp', 'goldredSupport'
              ], axis=1)



#matches.to_csv('test.csv')

x = gold[gold.NameType == 'golddiff'].describe().drop['std', 'count', '25%', '50%', '75%', 'max']
x.plot.hist()

plt.show()