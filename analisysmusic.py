import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


usuario = 'root'
contraseña = ''
host = 'localhost'
puerto = 3306
base_de_datos = 'Chinook'

conexion = create_engine(f"mysql+pymysql://{usuario}:{contraseña}@{host}:{puerto}/{base_de_datos}")


#Top 10 artistas con más canciones del género Rock

query = """
SELECT 
    album.Title AS album,
    track.Name AS track,
    artist.Name AS artist,
    Genre.Name AS genre
FROM track
INNER JOIN album ON track.AlbumId = album.AlbumId
INNER JOIN artist ON album.ArtistId = artist.ArtistId
INNER JOIN Genre ON track.GenreId = Genre.GenreId
WHERE Genre.Name = 'Rock';
"""

# 1.  Leer en un DataFrame
df = pd.read_sql(query, conexion)

# Agrupar por artista y contar cuántas canciones tiene cada uno
conteo_artistas = df.groupby("artist").count()["track"].reset_index()
conteo_artistas = conteo_artistas.sort_values(by="track", ascending=False).head(10)  # Top 10 artistas

# Graficar
plt.figure(figsize=(12, 6))
sns.barplot(data=conteo_artistas, x="artist", y="track")
plt.title("Top 10 artistas con más canciones del género Rock")
plt.xlabel("Artista")
plt.ylabel("Número de canciones")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()



# 2. top 10 generos con mas caciones 
query = """
SELECT Genre.Name AS genre, COUNT(*) AS num_tracks
FROM track
JOIN genre ON track.GenreId = genre.GenreId
GROUP BY Genre.Name
ORDER BY num_tracks DESC
LIMIT 10;
"""


df = pd.read_sql(query, conexion)


df = df.sort_values(by="num_tracks", ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(data=df, x="num_tracks", y="genre", palette="viridis")
plt.title("Top 10 géneros con más canciones")
plt.xlabel("Número de canciones")
plt.ylabel("Género")
plt.tight_layout()
plt.show()




# 3 canciones con artistas mas compradas
query = """
SELECT CONCAT(a.Name, ' - ', t.Name) AS cancion_artista, SUM(il.Quantity) AS total_comprada
FROM InvoiceLine il
JOIN Track t ON il.TrackId = t.TrackId
JOIN Album al ON t.AlbumId = al.AlbumId
JOIN Artist a ON al.ArtistId = a.ArtistId
GROUP BY cancion_artista
ORDER BY total_comprada DESC
LIMIT 10;
"""

# Leer datos
df = pd.read_sql(query, conexion)

# Ordenar para que el gráfico horizontal se vea de abajo hacia arriba
df = df.sort_values(by="total_comprada", ascending=True)

# Datos
etiquetas = df["cancion_artista"]
valores = df["total_comprada"]

# Graficar
plt.figure(figsize=(12, 6))
plt.barh(etiquetas, valores, color='mediumpurple', edgecolor='black')
plt.xlabel("Cantidad total comprada")
plt.title("Top 10 canciones más compradas (con artista)")
plt.tight_layout()
plt.grid(axis='x', linestyle='--', alpha=0.5)

# Mostrar
plt.show()



# 4. canciones  de Hip Hop/Rap con mas minutos de duracion

# Consulta: canciones de Salsa con mayor duración
query = """
SELECT t.Name AS track_name, t.Milliseconds
FROM Track t
JOIN Genre g ON t.GenreId = g.GenreId
WHERE g.Name = 'Hip Hop/Rap'
ORDER BY t.Milliseconds DESC
LIMIT 10;
"""

# Leer datos
df = pd.read_sql(query, conexion)

# Convertir duración a minutos
df["Minutes"] = df["Milliseconds"] / 60000


df = df.sort_values(by="Minutes", ascending=True)


plt.figure(figsize=(12, 6))
plt.barh(df["track_name"], df["Minutes"], color="coral", edgecolor="black")


plt.title("Top 10 canciones más largas del género Hip Hop/Rap")
plt.xlabel("Duración (minutos)")
plt.ylabel("Canción")
plt.tight_layout()
plt.grid(axis='x', linestyle='--', alpha=0.5)

# Mostrar
plt.show()



# 5. Obtener los 5 géneros con más canciones
top_genres_query = """
SELECT g.Name AS genre, COUNT(*) AS num_tracks
FROM track t
JOIN genre g ON t.GenreId = g.GenreId
GROUP BY g.Name
ORDER BY num_tracks DESC
LIMIT 3;
"""
top_genres_df = pd.read_sql(top_genres_query, conexion)
top_genres = top_genres_df["genre"].tolist()


placeholders = ", ".join(f"'{g}'" for g in top_genres)


query = f"""
SELECT g.Name AS genre, t.Milliseconds
FROM track t
JOIN genre g ON t.GenreId = g.GenreId
WHERE g.Name IN ({placeholders});
"""
df = pd.read_sql(query, conexion)


df["Minutes"] = df["Milliseconds"] / 60000


plt.figure(figsize=(12, 6))
sns.histplot(data=df, x="Minutes", hue="genre", bins='sturges', kde=True, alpha=0.5, palette='Set2')

plt.title("Distribución de duración de canciones por género (Top 5)")
plt.xlabel("Duración de la canción (minutos)")
plt.ylabel("Cantidad de canciones")
plt.tight_layout()
plt.show()