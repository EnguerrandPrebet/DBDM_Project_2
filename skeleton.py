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
                    )].loc[:, 'blueTop':'goldblueSupport']

print(matches.head())