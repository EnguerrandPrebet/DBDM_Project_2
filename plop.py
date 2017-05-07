
file = open("1st_data_filter.csv","r")
rows = file.read().split('\n')
file.close()
rows = rows[:-1] #Dernière ligne vide

"""for i in range(len(rows)):
    if not len(rows[i]):
        print(rows[i],i)""" #Ancien debug pour la ligne vide
        
mat = [row.split(';') for row in rows]

print(mat[0]) #Affichage du nom des colonnes

select_mat = [[eval(mat[0][j]) for j in [0,5,6]+list(range(9,24))]] + [ [eval(mat[i][j]) for j in [0,5,6]]+ [eval(eval(mat[i][j])) for j in range(9,24)] for i in range(1,len(mat))] #selection des colonnes en remplaçant le type string (double eval pour les listes)

print(select_mat[0]) #Affichage du nom des colonnes sélectionnées (à noter l'intérêt de l'eval pour virer les ")

print(select_mat[1][5][0],"lol") #Exemple 1er kill


new_mat = [[select_mat[i][j] for j in range(12)] for i in range(len(select_mat))]

##bKills en k/_/a

new_mat[0][6] = 'bAssists'

for i in range(1,len(select_mat)):
    if(len(select_mat[i][5][0]) == 0): #Pas de kill ou pas de data ?
        continue
    else:
        new_mat[i][5] = [0]*len(select_mat[i][5])
        new_mat[i][6] = [0]*len(select_mat[i][5])
        for j in range(len(select_mat[i][5])):
            #Temps,Kill (= 1), Assist (len - len([temps,mort,tueur]))
            new_mat[i][5][j] = select_mat[i][5][j][0]
            new_mat[i][6][j] = (select_mat[i][5][j][0],len(select_mat[i][5][j]) - 3)

print(new_mat[1][5],new_mat[1][6]) #Exemple de résultats de la transformation

#TODO: Trier la liste select_mat[1][i] pour rassembler ensuite les différents kills en k/_/a par créneau

##Rassemblement des objectifs (b)
print(select_mat[1][6:11])

new_mat[0][7] = 'bObjectives'

for i in range(1,len(select_mat)):
    new_mat[i][7] = sum(select_mat[i][6:11], [])
    
print(new_mat[1][7])

##rKills en k/_/a
#Recopiage des goldred
for i in range(len(select_mat)):
    new_mat[i][8] = select_mat[i][11]

#Kills
print(select_mat[0][12])

new_mat[0][9] = 'rKills'
new_mat[0][10] = 'rAssists'
for i in range(1,len(select_mat)):
    if(len(select_mat[i][12][0]) == 0): #Pas de kill ou pas de data ?
        continue
    else:
        new_mat[i][9] = [0]*len(select_mat[i][12])
        new_mat[i][10] = [0]*len(select_mat[i][12])
        for j in range(len(select_mat[i][12])):
            #Temps,Kill (= 1), Assist (len - len([temps,mort,tueur]))
            new_mat[i][9][j] = select_mat[i][12][j][0]
            new_mat[i][10][j] = (select_mat[i][12][j][0],len(select_mat[i][12][j]) - 3)

##Rassemblement des objectifs (b)
print(select_mat[1][13:18])

new_mat[0][11] = 'rObjectives'
for i in range(1,len(select_mat)):
    new_mat[i][11] = sum(select_mat[i][13:18], [])
    
print(new_mat[1][11])

##Réunion sous forme de tuples

#réunir selon les temps (on suppose que le dernier temps donné est plus grand que tous ceux de la data)
def func(data, dates):
    if(type(data[0]) != tuple):
        data.sort()
        data = [(d,1) for d in data]
    else:
        data.sort(key = lambda x:x[0])
    output = [0]*(len(dates))
    x = 0
    i = 0
    t = 0
    while (i < len(data) and t < len(dates)):
        if(data[i][0] < dates[t]):
            x += data[i][1]
            i += 1
        else:
            output[t] = x
            x = 0
            t += 1
    if(t == len(dates)):
        raise('Des objectifs ont eu lieu après le dernier temps: ' +str(data) + ' ' + str(dates))
        
    while(t < len(dates)):
        output[t] = x
        x = 0
        t += 1
    return output

#Calcul l'écart entre les dates de l'or
def func_gold(data, dates):
    
    output = [data[dates[0]]//1000] + [(data[min(dates[i],len(data)-1)] - data[dates[i-1]])//1000 for i in range(1,len(dates))]
    return output
    
    
print(func(new_mat[1][7],[7,15,20,25,30,35,40])) #Test de la fonction func

#Définit la liste des tuples correspondant à la suite d'événements pour une partie
def gen_word(game, dates):
    
    val1 = func_gold(game[4],dates) #goldblue
    val2 = func(game[5],dates) #bKills
    val3 = func(game[6],dates) #bAssist
    val4 = func(game[7],dates) #bObj
    if(len(val1) != len(val2) or len(val2) != len(val3) or len(val3) != len(val4)):
        print('Les différents paramètres ne sont pas scindés en autant d\'événements: ' + str(val1) + ' ' + str(val2) + ' ' + str(val3) + ' ' + str(val4))
        
    val5 = func_gold(game[8],dates) #goldblue
    val6 = func(game[9],dates) #bKills
    val7 = func(game[10],dates) #bAssist
    val8 = func(game[11],dates) #bObj
    
    return [(val1[i],val2[i],val3[i],val4[i],val5[i],val6[i],val7[i],val8[i]) for i in range(len(val1))]
    
print('\nColonnes :',new_mat[0])
print('Exemple :', new_mat[1])
print('Format : (Blue : k gold, kills, assists, objectives ; Red : k gold, kills assists, objectives)')
print("Résultats : ",gen_word(new_mat[1],[7,15,20,25,30,35,40]))
