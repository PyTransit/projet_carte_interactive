import dash
from dash import Dash,html,dcc,callback,Input,Output,callback_context,State,ALL
from plotly import express
import geopandas as gpd
from plotly.graph_objs import Figure

import datamanag
from datamanag import init_db,create_stops_div

# [id, route_long_name, stop_id, stop_name, stop_lon, stop_lat,
# operatorname, shortname, bookingrules, mode, nom_commune, code_insee, geometry]

# récupérer le GeoDataFrame
data = datamanag.data

# initialiser la base de données
#init_db(data) # doit être exécuter UNE SEULE FOIS

# création de la carte
fig = express.scatter_map(data,
                          lat=data.geometry.y,
                          lon=data.geometry.x,
                          width=1200,
                          height=800,
                          hover_name="Arrêt",
                          hover_data=["Ligne","Ville"],
                          zoom=11)

# création de l'app
app = Dash()

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},autosize=True)
my_map = dcc.Graph(figure=fig,id="my_map")
map_container = html.Div(
                children=my_map,
                id="map_container",
                style={
                    "flex":1,
                    "height": "100vh",
                    "margin": 0,
                    "padding": 0,
                    "overflow": "hidden"
})

panel = html.Div(children=create_stops_div(),
                 id="panel",
                 style={
                     "width":300,
                     "height":"calc(100vh - 10px)",
                     "overflow":"auto",
                     "padding":"0.8em",
                     "backgroundColor":"#FEFEF0"
                 })

whole_page = html.Div(children=[map_container,panel],
                      id="page",
                      style={"display":"flex","flexDirection":"row"}
                      )
app.layout = whole_page


@callback(
    Output("my_map","figure"),
    Input({"type":"stop","index":ALL},"n_clicks"),
    State("my_map","figure")
)
def stop_clicked(clicks, figx):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update

    # récupérer l'id de l'arrêt
    idx = int(ctx.triggered_id.index)
    # récupérer les infos
    stop = data.iloc[idx]
    lat = float(stop["stop_lat"])
    lon = float(stop["stop_lon"])

    # mettre à jour la carte
    new_fig = Figure(figx)
    new_fig.update_layout(
        map=dict(style="carto-voyager",center=dict(lat=lat, lon=lon),zoom=16)
    )
    return new_fig

app.run(debug=True)