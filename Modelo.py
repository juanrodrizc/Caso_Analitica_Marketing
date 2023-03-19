import os 
import sqlite3 as sql
import pandas as pd
import joblib 
from sklearn import neighbors
from ipywidgets import interact ## para análisis interactivo

conn=sql.connect('db_movies')
cur=conn.cursor()

#### ver tablas disponibles en base de datos ###

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
cur.fetchall()

full = pd.read_sql("SELECT * FROM full_ratings; ",conn)
movies2 = pd.read_sql("SELECT * FROM movies2; ",conn)

full2= movies2.iloc[:,4:] #Tabla de datos solo con dummyes 
### 2.1 Sistema de recomendación basado en contenido KNN un solo producto visto ###

##### ### entrenar modelo #####
#Géneros, rating y user 
model = neighbors.NearestNeighbors(n_neighbors=11, metric='cosine')
model.fit(full2)
dist, idlist = model.kneighbors(full2)

distancias=pd.DataFrame(dist)
id_list=pd.DataFrame(idlist)

movie_name=str(input('Ingrese la película para buscar similares',))

def MovieRecommender(movie_name = list(movies2['title'].value_counts().index)): #Se necesitan las películas de la bd
    movie_list_name = []  #Se define un vector vacío
    movie_id = movies2[movies2['title'] == movie_name].index # Lista de los id de las peliculas
    movie_id = movie_id[0]  #El primer id es 0
    for newid in idlist[movie_id]: #Se asigna un nuevo id teniendo en cuenta lo parecido que son
        movie_list_name.append(movies2.loc[newid].title)
    return movie_list_name


print(interact(MovieRecommender))

