from cmath import nan
from matplotlib.pyplot import axis
import requests
import json
import csv
import pandas as pd
import numpy as np
from datetime import datetime
import datetime
import plotly.express as px
import plotly.graph_objects as go
import dash
#import dash_leaflet as dl
#pd.set_option('display.max_rows', 10)
########################################################################################################################
# IMPORTATION ET LECTURE DES DONNEES EN TEMPS REEL DEPUIS L'API OPEN DATA PARIS
########################################################################################################################

# L'ecture de l'url dans lesquels les données sont présentes
r = requests.get("https://opendata.paris.fr/api/records/1.0/search/?dataset=belib-points-de-recharge-pour-vehicules-electriques-disponibilite-temps-reel&q=&rows=9999&sort=code_insee_commune&facet=statut_pdc&facet=last_updated&facet=arrondissement")
#r.encoding
#Création d'un objet data contenant les données de l'url
data = r.json()
#Dans l'objet data on filtre sur "records" pour uniquement récupérer les données 
sites = data["records"]

path = "/Users/ganza/OneDrive/Bureau/Projet_prerso/python/pythonProject/pythonProject/bornes_recharge_application_dash/data"
path_token = "/Users/ganza/OneDrive/Bureau/Projet_prerso/python/pythonProject/pythonProject/bornes_recharge_application_dash"

########################################################################################################################
# ENREGISTREMENT ET MISE EN FORME DES DONNEES
########################################################################################################################
"""
Création d'un ficher en mode écriture "w" s'il n'existe pas afin d'enregistrer les données.
with open clot automatiquement le fichier après instruction.
"""

#création du chemin vers lequel pointeront les données
with open(path + '/stations.csv', 'w', newline='', encoding='utf-8') as file:
    #Ecrire dans le ficher avec les noms de colonnes
    writer = csv.writer(file,delimiter=',')
    #on crait les colonnes du fichier
    writer.writerow(['adresse_station', 'arrondissement', 'statut_pdc', 'code_insee_commune', 'coordonneesxy', 'lat', 'long','id_pdc', 'last_date_time_update'])
    #on itère dans l'objet data pour récuperer les données présentes dans le fields (un niveau sous records)
    try :
        for elt in sites:
            adress = elt["fields"]["adresse_station"]
            #print(adress)
            arrondissement = elt['fields']['arrondissement']
            # print(arrondissement)
            statut = elt['fields']['statut_pdc']
            # print(statut)
            cp = elt['fields']['code_insee_commune']
            # print(cp)
            lat_long = elt['fields']['coordonneesxy']
            # print(lat_long)
            lat = elt['fields']['coordonneesxy'][0]
            # print(lat)
            long = elt['fields']['coordonneesxy'][1]
            # print(long)
            id_pdc = elt['fields']['id_pdc']
            # print(id_pdc)

            date = elt['fields']['last_updated']
            
            last_date_time_update = datetime.datetime.fromisoformat(date)
    #        last_date_update = last_date_time_update.date()
    #        last_time_update = last_date_time_update.time()
            
            #on remplit les colonnes avec les variables ci-dessus
            writer.writerow([adress, arrondissement, statut, cp, lat_long, lat, long, id_pdc, last_date_time_update])
    except KeyError:
        pass

"""On récupère les données du fichier csv et on met les dates en index afin
    d'en extraire plus facilement l'heure (utile pour l'histogram)
"""
df = pd.read_csv(path + '/stations.csv', index_col= 'last_date_time_update',parse_dates=True)
print(df.head())

# On crait une colonne heure
df['last_update_by_hour'] = df.index.hour

# Pour chaque station, on récupère le nombre de bornes disponible
df['nb_charging_stations'] = df.groupby(by='adresse_station')['adresse_station'].transform('count')



"""
Pour chaque stations nous allons messurer son occupation.

"""
def statut_count(df):
    
        if  df.statut_pdc == "Occupé (en charge)" :
            return 1
        else:
            None

df["occupation (1=yes, 0=no)"] = df.apply(statut_count, axis=1)

df["occupation (1=yes, 0=no)"] = df.groupby(by="adresse_station")["occupation (1=yes, 0=no)"].transform('count')



"""
Pour chaque arrondissements, nous voulons messurer le taux d'occupation des stations de recharges
"""
#dictionnaire contenant le nombre de bornes occupées pour chaque arrondissements
from collections import defaultdict
d = defaultdict(list)
for k,v in zip(df.code_insee_commune,df["occupation (1=yes, 0=no)"]):
    if v == 1:
        d[k].append(v)
df_occupation_by_dept = pd.DataFrame(d.items(), columns=['dept', 'nb station anvailable']) 
#df_occupation_by_dept

#dictionnaire contenant le nombre de bornes de recharge par arrondissements
d= defaultdict(list)
for k,v in zip(df.code_insee_commune,df['nb_charging_stations']):     
        d[k].append(v)
        
for k,v in d.items():
        d[k] = sum(v)  
df_nb_charging_station_by_dept = pd.DataFrame(d.items(), columns=['dept', 'nb of charging station']) 
#df_nb_charging_station_by_dept

#Création du dataframe mesurant le taux d'occupation pour chaque arrondissement
#df_nb_charging_station_by_dept['tx_occupation_by_dept'] = ((df_occupation_by_dept['nb station anvailable']/df_nb_charging_station_by_dept['nb of charging station'])*100).round(2)



        
# https://opendata.paris.fr/explore/dataset/belib-points-de-recharge-pour-vehicules-electriques-disponibilite-temps-reel/table/?disjunctive.statut_pdc&disjunctive.arrondissement&sort=id_pdc&dataChart=eyJxdWVyaWVzIjpbeyJjaGFydHMiOlt7InR5cGUiOiJjb2x1bW4iLCJmdW5jIjoiQ09VTlQiLCJzY2llbnRpZmljRGlzcGxheSI6dHJ1ZSwiY29sb3IiOiIjRkZDRDAwIn1dLCJ4QXhpcyI6Imxhc3RfdXBkYXRlZCIsIm1heHBvaW50cyI6IiIsInRpbWVzY2FsZSI6ImhvdXIiLCJzb3J0IjoiIiwiY29uZmlnIjp7ImRhdGFzZXQiOiJiZWxpYi1wb2ludHMtZGUtcmVjaGFyZ2UtcG91ci12ZWhpY3VsZXMtZWxlY3RyaXF1ZXMtZGlzcG9uaWJpbGl0ZS10ZW1wcy1yZWVsIiwib3B0aW9ucyI6eyJkaXNqdW5jdGl2ZS5zdGF0dXRfcGRjIjp0cnVlLCJkaXNqdW5jdGl2ZS5hcnJvbmRpc3NlbWVudCI6dHJ1ZSwic29ydCI6ImNvZGVfaW5zZWVfY29tbXVuZSJ9fX1dLCJkaXNwbGF5TGVnZW5kIjp0cnVlLCJhbGlnbk1vbnRoIjp0cnVlfQ%3D%3D&rows=999&timezone=&basemap=jawg.dark&location=12,48.86471,2.33974

########################################################################################################################
# CREATION DE LA MAP ET DES GRAPH INTERACTIFS
########################################################################################################################

"""
Création de la web app avec la librairie Dash (pour la web app intéractive)
et plotly (pour la création de graphiques)
"""
colorscale=[
             [0, "#F4EC15"],
             [0.04167, "#DAF017"],
             [0.0833, "#BBEC19"],
             [0.125, "#9DE81B"],
             [0.1667, "#80E41D"],
             [0.2083, "#66E01F"],
             [0.25, "#4CDC20"],
             [0.292, "#34D822"],
             [0.333, "#24D249"],
             [0.375, "#25D042"],
             [0.4167, "#26CC58"],
             [0.4583, "#28C86D"],
             [0.50, "#29C481"],
             [0.54167, "#2AC093"],
             [0.5833, "#2BBCA4"],
             [1.0, "#613099"],
             ]
#df.code_insee_commune = df.code_insee_commune.astype(str)
#On génère une map avec mapbox depuis la librairie plotly
mapbox_access_token = px.set_mapbox_access_token(open(path_token + "/mapbox_token.txt").read())
fig = px.scatter_mapbox(df, lat='lat', lon='long', size=((df["occupation (1=yes, 0=no)"]/df["nb_charging_stations"])*100).round(2),
                        mapbox_style='carto-darkmatter', animation_group='adresse_station',opacity=0.20,
                        labels='nb_charging_stations',hover_data=['nb_charging_stations'], color="code_insee_commune",
                        # hover_data=[df['statut_pdc'][i] for i in range(df.shape[0])],
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=12, zoom=11.2)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0,})

fig.update_layout(coloraxis_showscale=False)
#fig.update_traces(hovertemplate=None)
fig.update_coloraxes(colorscale=colorscale)




############################### HISTOGRAM ###############################
'''
On cherche ici à afficher l'occupation des bornes de recharge.
On va donc créer une nouvelle colonnes afin d'extraire si "oui" ou non la station est disponible.
si "oui", on récupère l'heure

'''

nb_disponibility_station_by_hours = []
for a,b in zip(df.last_update_by_hour, df["occupation (1=yes, 0=no)"]):
    if b == 1:
        nb_disponibility_station_by_hours.append(a)

hours_hist = ([i for i in df.last_update_by_hour] + [i for i in range(0,24) if i not in nb_disponibility_station_by_hours])
fig_hist = px.histogram(df, x=hours_hist,text_auto=True)
#Espacer les bars
fig_hist.update_layout(bargap=0.01,showlegend=False)




###################### PROBLEMES ######################
#Pourquoi y a-t'il tant d'occupation à 2h ?
#print(hours_hist[hours_hist == 2])





# CREATION DA L APPLICATION DASH
from dash import Dash, html, dcc
import plotly.express as px
from dash.dependencies import Input, Output

# Definir les paramettres du dropdown

dropdow_map_options = [dict(label=x, value=x)
                       for x in df['code_insee_commune'].unique()]

app = Dash(__name__)

app_colors = {
    'background': '#343332',
    'text': '#FFFFFF'
}

fig.update_layout(
    plot_bgcolor=app_colors['background'],
    paper_bgcolor=app_colors['background'],
    font_color=app_colors['text'],
    margin={"r":0,"t":0,"l":0,"b":0}
)

fig_hist.update_layout(
    plot_bgcolor=app_colors['background'],
    paper_bgcolor=app_colors['background'],
    font_color=app_colors['text'],
    margin={"r":0,"t":0,"l":0}
)

app.title = "Stations de recharge Paris"

app.layout = html.Div(style={'background-color': app_colors['background'],
                             'paper_bgcolor' :app_colors['background'],
                             },
                      className= "content",
                      children=[
                        html.Div(
                            className='all_compenents',
                            children=[

                              #Left components : H1 dropdown
                              html.Div(
                                  className="div_left_components",
                                       children=[
                                           html.H1(
                                            "Carte des bornes de recharge à Paris",
                                             style={
                                                  'textAlign': 'center',
                                                  'color': app_colors['text'],
                                                  'margin': '0%'
                                              }
                                          ),
                                           dcc.Dropdown(
                                               id='DDMap',
                                                value= df.statut_pdc.unique()[0:2],
                                                options=dropdow_map_options

                                                        )
                                       ]
                                    ),



                          #Check list
                          #     html.Div(
                          #         className='check_list',
                          #         children=[
                          #        dcc.Checklist(
                          #               df.statut_pdc.unique(), df.statut_pdc.unique()[0:2],
                          #               inline=False,
                          #
                          #               style={
                          #
                          #                   'color': app_colors['text']
                          #               }
                          #
                          #           )]
                          # ),

                          #Map hist
                          html.Div(className='map_hist',
                                   children=[
                                       html.Div(
                                           dcc.Graph(className='map',
                                               figure=fig
                                           )
                                       ),
                                       html.Div(

                                               dcc.Graph(className='hist',
                                                   figure=fig_hist
                                               )

                                    )
                                   ]
                                )


                        ])

                      ]#end children

                )


app.run_server(debug=True, use_reloader=True)
