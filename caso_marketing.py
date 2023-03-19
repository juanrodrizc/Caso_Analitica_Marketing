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