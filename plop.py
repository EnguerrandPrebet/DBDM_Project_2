
file = open("1st_data_filter.csv","r")
rows = file.read().split('\n')
file.close()
rows = rows[:-1] #Dernière ligne vide

"""for i in range(len(rows)):
    if not len(rows[i]):
        print(rows[i],i)""" #Ancien debug pour la ligne vide
        
mat = [row.split(';') for row in rows]

print(mat[0]) #Affichage du nom des colonnes

select_mat = [[eval(mat[0][j]) for j in [0,5,6]+list(range(10,24))]] + [ [eval(mat[i][j]) for j in [0,5,6]]+ [eval(eval(mat[i][j])) for j in range(10,24)] for i in range(1,len(mat))] #selection des colonnes en remplaçant le type string (double eval pour les listes)

print(select_mat[0]) #Affichage du nom des colonnes sélectionnées (à noter l'intérêt de l'eval pour virer les ")

print(select_mat[1][4][0]) #Exemple 1er kill

##bKills en k/_/a

for i in range(1,len(select_mat)):
    if(len(select_mat[i][4][0]) == 0): #Pas de kill ou pas de data ?
        continue
    else:
        for j in range(len(select_mat[i][4])):
            select_mat[i][4][j] = (select_mat[i][4][j][0],1,len(select_mat[i][4][j]) - 3) #Temps,Kill (= 1), Assist (len - len([temps,mort,tueur]))

print(select_mat[1][4]) #Exemple de résultats de la transformation

#TODO: Trier la liste select_mat[1][i] pour rassembler ensuite les différents kills en k/_/a par créneau