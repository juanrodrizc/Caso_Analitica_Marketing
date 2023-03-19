
import os 
import sqlite3 as sql
import pandas as pd
import datetime
# conda install mlxtend
# !pip install mlxtend
from mlxtend.preprocessing import TransactionEncoder

from PIL import Image
i=Image.open('Diseño de la solución.png','r') # imagen en color 
i.show()

### para ver y cambiar directorio de trabajo
os.getcwd()
os.chdir('C:/Users/Asus/Documents/Analitica 3 Caso Marketing')

###### para ejecutar sql y conectarse a bd ###
conn=sql.connect('db_movies')
cur=conn.cursor()

############ cargar tablas ####
movies = pd.read_sql("SELECT * FROM movies; ",conn)
ratings = pd.read_sql("SELECT * FROM ratings; ",conn)

# dado que la fecha esta en formato timestamp, lo que implica que esta dada en segundos, por ello lo llevamos a formato fecha 
ratings["timestamp"]  = ratings["timestamp"].apply(lambda x: datetime.datetime.fromtimestamp(x))


# Separamos el año de lanzamiento de las películas

import re
# Definir patrón regex para extraer el año
patron_regex = r'\((\d{4})\)'

# Extraer año de cada fila en la columna 'texto'
movies['year'] = movies['title'].apply(lambda x: re.findall(patron_regex, x)[0] if re.findall(patron_regex, x) else None)
null_rows = movies[movies.isna().any(axis=1)]
movies['year'].fillna(0, inplace =True)
movies['year'] = movies['year'].astype(int)
# Eliminar el año de la columna 'texto'
movies['title'] = movies['title'].apply(lambda x: re.sub(patron_regex, '', x))


# Separamos los generos de las películas

genres=movies['genres'].str.split('|')
te = TransactionEncoder()
genres = te.fit_transform(genres)
genres = pd.DataFrame(genres, columns = te.columns_)
genres = genres.replace({True: 1, False: 0})

del(movies["genres"])

#movies = movies.merge(genres, how='outer', left_on=None, right_on=None, left_index=False, right_index=False)

movies = pd.concat([movies, genres], axis = 1)

movies.info()


############################################################

