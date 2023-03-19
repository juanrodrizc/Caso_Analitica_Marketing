import os 
import sqlite3 as sql
import pandas as pd

### para ver y cambiar directorio de trabajo
os.getcwd()
os.chdir('C:\\Users\\ASUS\\Documents\\ANALITICA III\\Caso Marketing')

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
ratings["rating"].unique() 
ratings["rating"].value_counts()

##### Descripción base de ratings

###calcular la distribución de calificaciones
cr=pd.read_sql(""" select 
                          rating, 
                          count(*) as conteo 
                          from book_ratings
                          group by "Book-Rating"
                          order by conteo desc""", conn)





