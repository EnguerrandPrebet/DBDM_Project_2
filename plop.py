
file = open("1st_data_filter.csv","r")
rows = file.read().split('\n')
rows = rows[:-1] #Dernière ligne vide
for i in range(len(rows)):
    if not len(rows[i]):
        print(rows[i],i)
mat = [row.split(';') for row in rows]
print(mat[0])

select_mat = [[eval(mat[0][j]) for j in [0,5,6]+list(range(10,24))]] + [ [eval(mat[i][j]) for j in [0,5,6]]+ [eval(eval(mat[i][j])) for j in range(10,24)] for i in range(1,len(mat))] #sélection des colonnes (double eval pour les listes)
print(select_mat[0])

dict = {select_mat[0][i]: [select_mat[j][i] for j in range(len(select_mat))] for i in range(len(select_mat[0]))}

file.close()