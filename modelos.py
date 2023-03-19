import sqlite3 as sql
import pandas as pd
from sklearn import neighbors
from ipywidgets import interact ## para análisis interactivo
import numpy as np

conn=sql.connect('db_movies')
cur=conn.cursor()

#### ver tablas disponibles en base de datos ###
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
cur.fetchall()

movies2 = pd.read_sql("SELECT * FROM movies2; ",conn)

dummies = movies2.iloc[:,4:] #Tabla de datos solo con dummies 

"""--- Sistema de recomendación basado en contenido KNN un solo producto visto ---"""

##### ### entrenar modelo #####
#Géneros, rating y user 
model = neighbors.NearestNeighbors(n_neighbors=11, metric='cosine')
model.fit(dummies)
dist, idlist = model.kneighbors(dummies)

distancias=pd.DataFrame(dist)
id_list=pd.DataFrame(idlist)

def MovieRecommender(movie_name): #Se necesitan las películas de la bd
    movie_list_name = []  #Se define un vector vacío
    movie_id = movies2[movies2['title'] == movie_name].index # Lista de los id de las peliculas
    movie_id = movie_id[0]  #El primer id es 0
    for newid in idlist[movie_id]: #Se asigna un nuevo id teniendo en cuenta lo parecido que son
        movie_list_name.append(movies2.loc[newid].title)
    return np.array(movie_list_name)

recomendaciones=[]
for i in movies2['title']: 
    recomendaciones.append(MovieRecommender(i))

tabla_recomendaciones=pd.DataFrame(data=movies2['title'])
tabla_recomendaciones['recomendaciones']=recomendaciones
print(tabla_recomendaciones)

"""---Sistema de recomendación basado en contenido para todo lo visto por el usuario--"""

usuario=pd.read_sql('select distinct (userId) from full',conn)

def recomendar(user_id):
    
    ratings=pd.read_sql('select *from ratings_final where userId=:user',conn, params={'user':user_id})
    movies_r=ratings['movieId'].to_numpy()
    dummies[['movieId','title']]=movies2[['movieId','title']]
    mov=dummies[dummies['movieId'].isin(movies_r)]
    mov=mov.drop(columns=['movieId','title'])
    mov["indice"]=1 ### para usar group by y que quede en formato pandas tabla de centroide
    centroide=mov.groupby("indice").mean()
    
    
    mov2=dummies[~dummies['movieId'].isin(movies_r)]
    mov2=mov2.drop(columns=['movieId','title'])
    model=neighbors.NearestNeighbors(n_neighbors=11, metric='cosine')
    model.fit(mov2)
    dist, idlist = model.kneighbors(centroide)
    
    ids=idlist[0]
    recomend_b=movies2.loc[ids][['title','movieId']]
    vistos=movies2[movies2['movieId'].isin(movies_r)][['title','movieId']]
    
    return np.array(recomend_b)

recom_user=[]
for i in usuario['userId']: 
    recom_user.append(recomendar(i))

tabla_recom_user=pd.DataFrame(data=usuario['userId'])
tabla_recom_user['recomendaciones con movieId']=recom_user
print(tabla_recom_user)
