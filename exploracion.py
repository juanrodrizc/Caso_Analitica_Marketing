import os 
import sqlite3 as sql
import pandas as pd
import plotly.graph_objs as go 
import matplotlib.pyplot as plt
import plotly.express as px
import matplotlib 
import funciones as fn

#matplotlib.use('Qt5Agg')

### para ver y cambiar directorio de trabajo
os.getcwd()
os.chdir('C:/Users/Asus/Documents/Analitica 3 Caso Marketing')

###### para ejecutar sql y conectarse a bd ###
conn=sql.connect('db_movies')
cur=conn.cursor()

### para verificar las tablas que hay disponibles
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cur.fetchall())

############ cargar tablas ####
movies = pd.read_sql("SELECT * FROM movies; ",conn)
ratings = pd.read_sql("SELECT * FROM ratings; ",conn)


### Identificar campos de cruce y verificar que estén en mismo formato ####
### verificar duplicados

movies.info() # Se observa que tiene 3 campos, el id de la película, el título y el género
movies.duplicated().sum() #No se tienen duplicados 

ratings.info()
ratings.duplicated().sum() #No se tienen duplicados

movies["genres"].unique() #Separar los géneros que estan indicados con |
ratings["rating"].unique() #Los valores están comprendidos entre 0 y 5. La calificación más baja es de 0.5
ratings["rating"].value_counts()

##### Descripción base de ratings

###calcular la distribución de ratingS
dr=pd.read_sql(""" select 
                          rating, 
                          count(*) as conteo 
                          from ratings
                          group by rating
                          order by conteo asc""", conn)                          

# Graficar las ventas por categoría de productos
dr.plot(kind='bar', x='rating', y='conteo', legend=None)
plt.title('Cantidad de usuarios por rating')
plt.xlabel('Rating')
plt.ylabel('Usuarios')
plt.show()            
# La mayoría de usuarios considera que las películas son regulares o buenas las películas

### calcular cada usuario cuátos películas calificó
rating_users=pd.read_sql(''' select userId,
                         count(*) as cnt_rat
                         from ratings
                         group by userId
                         order by cnt_rat asc
                         ''',conn )

#fig  = px.histogram(rating_users, x= 'cnt_rat', title= 'Hist frecuencia de numero de calificaciones por usuario')
#fig.show() 

# Graficar histograma de frecuencia de numero de calificaciones por usuario
plt.hist(rating_users, bins=15)
plt.title('Hist frecuencia de numero de calificaciones por usuario')
plt.xlabel('Calificaciones')
plt.ylabel('Usuarios')
plt.show()


rating_users.describe()
#El valor máximo de películas calificadas por un usuario es demasiado grande

#### filtrar usuarios con más de 100 películas calificadas (para tener calificaion confiable) y los que tienen mas de mill porque pueden ser no razonables
rating_users2=pd.read_sql(''' select userId,
                         count(*) as cnt_rat
                         from ratings
                         group by userId
                         having cnt_rat >=100 and cnt_rat <=1000
                         order by cnt_rat asc
                         ''',conn )

### ver distribucion despues de filtros,ahora se ve mas razonables
rating_users2.describe()

### graficar distribucion despues de filtrar datos
plt.hist(rating_users2, bins=15)
plt.title('Hist frecuencia de numero de calificaciones por usuario')
plt.xlabel('Calificaciones')
plt.ylabel('Usuarios')
plt.show()

#### verificar cuantas calificaciones tiene cada película
rating_movies=pd.read_sql(''' select movieId,
                         count(*) as cnt_rat
                         from ratings
                         group by movieId
                         order by cnt_rat desc
                         ''',conn )

### analizar distribucion de calificaciones por película
rating_movies.describe()

### graficar distribucion

plt.hist(rating_movies, bins=15)
plt.title('Hist frecuencia de numero de calificaciones por película')
plt.xlabel('Calificaciones')
plt.ylabel('Películas')
plt.show()
 
####Filtrar películas que tengan más de 50 calificaciones y usuarios que no tengan más de 10 libros calificados
rating_movies2=pd.read_sql(''' select movieId,
                         count(*) as cnt_rat
                         from ratings
                         group by movieId
                         having cnt_rat>=50
                         order by cnt_rat desc
                         ''',conn )

rating_movies2.describe()


### graficar distribucion despues de filtrar datos
plt.hist(rating_movies2, bins=15)
plt.title('Hist frecuencia de numero de calificaciones por película')
plt.xlabel('Calificaciones')
plt.ylabel('Películas')
plt.show()

###########
fn.ejecutar_sql('preprocesamientos.sql', cur)

cur.execute("select name from sqlite_master where type='table' ")
cur.fetchall()

