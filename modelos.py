import sqlite3 as sql
import pandas as pd
from sklearn import neighbors
import numpy as np
from surprise import Reader, Dataset
from surprise import KNNBasic, KNNWithMeans, KNNWithZScore, KNNBaseline, SVD
from surprise.model_selection import cross_validate, GridSearchCV
from surprise.model_selection import train_test_split
import preprocesamientos as pre

conn=sql.connect('db_movies')
cur=conn.cursor()

#### ver tablas disponibles en base de datos ###
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
cur.fetchall()

movies2 = pd.read_sql("SELECT * FROM movies2; ",conn)

dummies = movies2.iloc[:,3:] #Tabla de datos dummies y el año
pre.escalar(dummies)

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

""" Sistema de recomendación filtro colaborativo basado en usuario """


ratings=pd.read_sql('select * from ratings_final', conn)

###### leer datos desde tabla de pandas
reader = Reader(rating_scale=(0, 5))

###las columnas deben estar en orden estándar: user item rating
data   = Dataset.load_from_df(ratings[['userId','movieId','rating']], reader)



models=[KNNBasic(),KNNWithMeans(),KNNWithZScore(),KNNBaseline()] 
results = {}

for model in models:
 
    CV_scores = cross_validate(model, data, measures=["MAE","RMSE"], cv=5, n_jobs=-1)  
    result = pd.DataFrame.from_dict(CV_scores).mean(axis=0).\
             rename({'test_mae':'MAE', 'test_rmse': 'RMSE'})
    results[str(model).split("algorithms.")[1].split("object ")[0]] = result


performance_df = pd.DataFrame.from_dict(results).T
performance_df.sort_values(by='RMSE')


param_grid = { 'k':[40,80,60],
              'min':[30,40],
              'sim_options' : {'name': ['msd','cosine'], \
                                'min_support': [5], \
                                'user_based': [False, True]}
             }

gridsearchKNNBaseline = GridSearchCV(KNNBaseline, param_grid, measures=['rmse'], \
                                      cv=2, n_jobs=2)
                                    
gridsearchKNNBaseline.fit(data)

gridsearchKNNBaseline.best_params["rmse"]
gridsearchKNNBaseline.best_score["rmse"]
gs_model=gridsearchKNNBaseline.best_estimator['rmse'] ### mejor estimador de gridsearch


################# Realizar predicciones

trainset = data.build_full_trainset() ### esta función convierte todos los datos en entrenamiento
model=gs_model.fit(trainset) ## se entrena sobre todos los datos posibles


predset = trainset.build_anti_testset() ### crea una tabla con todos los usuarios y las películas que no han visto
#### en la columna de rating pone el promedio de todos los rating, en caso de que no pueda calcularlo para un item-usuario

predictions = model.test(predset) ### función muy pesada, hace las predicciones de rating para todos las películas que no ha visto un usuario
### la funcion test recibe un test set constriuido con build_test method, o el que genera crosvalidate

predictions_df = pd.DataFrame(predictions) ### esta tabla se puede llevar a una base donde estarán todas las predicciones
predictions_df.shape
predictions_df.head()
predictions_df['r_ui'].unique() ### promedio de ratings
predictions_df.sort_values(by='est',ascending=False)

####### la predicción se puede hacer para una película puntual
model.predict(uid='171', iid='213',r_ui='3.568656')

##### funcion para recomendar las 10 películas con mejores predicciones y llevar base de datos para consultar resto de información
def recomendaciones(user_id,n_recomend=10):
    
    predictions_userID = predictions_df[predictions_df['uid'] == user_id].\
                    sort_values(by="est", ascending = False).head(n_recomend)

    recomendados = predictions_userID[['iid','est']]
    recomendados.to_sql('reco',conn,if_exists="replace")
    
    recomendados=pd.read_sql('''select a.*, b.title 
                             from reco a left join movies2 b
                             on a.iid=b.movieId ''', conn)

    return(recomendados)

 
us1=recomendaciones(user_id=171,n_recomend=20)
