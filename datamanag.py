import geopandas as gpd
from dash import html
from functools import lru_cache
import sqlite3

# [id, route_long_name, stop_id, stop_name, stop_lon, stop_lat,
# operatorname, shortname, bookingrules, mode, nom_commune, code_insee, geometry]

# lecture du GeoJSON
data = gpd.read_file("arrets-lignes_kabs.geojson")

# renomme les colonnes chelous
data = data.rename(columns={
    "stop_name":"Arrêt",
    "route_long_name":"Ligne",
    "nom_commune":"Ville"
})

def init_db(data):
    # créer la base de données
    db = sqlite3.connect("kabs.db")
    curs = db.cursor()
    # créer la table
    curs.execute("""CREATE TABLE stops(
            stop_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            longitude REAL NOT NULL,
            latitude REAL NOT NULL,
            city TEXT NOT NULL,
            num_line TEXT NOT NULL
    )""")

    # conservation des données importantes
    filtered_data = [(id,
                      row["Arrêt"],
                      row["stop_lon"],
                      row["stop_lat"],
                      row["Ville"],
                      row["Ligne"]) for id,row in data.iterrows()]
    # insérer les données
    curs.executemany("""
        INSERT INTO stops(stop_id,name,longitude,latitude,city,num_line)
        VALUES (?,?,?,?,?,?)
    """,filtered_data)

    # enregistrement
    db.commit()
    db.close()

@lru_cache(maxsize=1)
def create_stops_div():
    db = sqlite3.connect("kabs.db")
    curs = db.cursor()

    curs.execute("SELECT name,city,num_line,stop_id FROM stops ORDER BY name")
    stops = curs.fetchall()
    db.close() # question de sécurité

    # 0=name 1=city 2=num_line 3=stop_id
    divs = [
        html.Div(children=[
            html.H3(children=f"{stop[0]}"),
            html.P(children=f"{stop[1]}"),
            html.P(children=f"{stop[2]}")
        ],
            id={"type":"stop","index":stop[3]},
            n_clicks=0,
            style={"fontSize":"1em","border":"1px solid black","padding":"5px","cursor":"pointer"})
    for stop in stops]

    return divs

