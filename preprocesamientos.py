
import os 
import sqlite3 as sql
import pandas as pd
import datetime
import re
# conda install mlxtend
# !pip install mlxtend
from mlxtend.preprocessing import TransactionEncoder
from sklearn.preprocessing import MinMaxScaler

### para ver y cambiar directorio de trabajo
os.getcwd()
#os.chdir('C:/Users/Asus/Documents/Analitica 3 Caso Marketing') --> Cambiar Ruta de archivos

###### para ejecutar sql y conectarse a bd ###
conn=sql.connect('db_movies')
cur=conn.cursor()

############ cargar tablas ####
movies = pd.read_sql("SELECT * FROM movies; ",conn)
ratings = pd.read_sql("SELECT * FROM ratings; ",conn)

# dado que la fecha esta en formato timestamp, lo que implica que esta dada en segundos, por ello lo llevamos a formato fecha
def timestamp(ratings): 
    ratings["timestamp"]  = ratings["timestamp"].apply(lambda x: datetime.datetime.fromtimestamp(x))

# Separamos el año de lanzamiento de las películas
def split_year(movies):
    # Definir patrón regex para extraer el año
    patron_regex = r'\((\d{4})\)'
    
    # Extraer año de cada fila en la columna 'title'
    movies['year'] = movies['title'].apply(lambda x: re.findall(patron_regex, x)[0] if re.findall(patron_regex, x) else None)
    movies['year'].fillna(0, inplace =True)
    movies['year'] = movies['year'].astype(int)
    
    # Eliminar el año de la columna 'title'
    movies['title'] = movies['title'].apply(lambda x: re.sub(patron_regex, '', x))

def split__gender(movies):   
    # Separamos los generos de las películas
    genres=movies['genres'].str.split('|')
    te = TransactionEncoder()
    genres = te.fit_transform(genres)
    genres = pd.DataFrame(genres, columns = te.columns_)
    genres = genres.replace({True: 1, False: 0})
    
    # Eliminar columna original 
    del(movies["genres"])
    movies = pd.concat([movies, genres], axis = 1)
    return movies

def escalar(movies):
    sc=MinMaxScaler()
    movies[["year"]]=sc.fit_transform(movies[['year']])
    return movies

#Quitarles el espacio a los nombres 
#Poner el The de primero


