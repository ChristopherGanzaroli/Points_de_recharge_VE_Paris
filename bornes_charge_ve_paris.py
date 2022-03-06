import requests
import json
import csv
import pandas as pd
import numpy as np
from datetime import datetime
import datetime
import plotly.express as px
import plotly.graph_objects as go
# In[2]:


pd.set_option('display.max_rows', 10)

# In[3]:


r = requests.get("https://opendata.paris.fr/api/records/1.0/search/?dataset=belib-points-de-recharge-pour-vehicules-electriques-disponibilite-temps-reel&q=&rows=9999&sort=code_insee_commune&facet=statut_pdc&facet=last_updated&facet=arrondissement")
data = r.json()
json.dumps(data, indent=4, sort_keys=False)

# print(data)

# In[4]:

path = "/Users/ganza/OneDrive/Bureau/Projet_prerso/python/pythonProject/pythonProject/bornes_recharge_application_dash/data"
path_token = "/Users/ganza/OneDrive/Bureau/Projet_prerso/python/pythonProject/pythonProject/bornes_recharge_application_dash"

# In[7]:





#with open(path + '/data.json', 'w') as json_file:
#     json.dump(data, json_file, indent=4, sort_keys=False)

# # In[8]:

sites = data['records']

with open(path + '/stations.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file,delimiter=',')
    writer.writerow(['adresse_station', 'arrondissement', 'statut_pdc', 'code_insee_commune', 'coordonneesxy', 'lat', 'long','id_pdc', 'last_date_time_update'])
    try :
        for elt in sites:
            adress = elt["fields"]["adresse_station"]
            print(adress)
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

            writer.writerow([adress, arrondissement, statut, cp, lat_long, lat, long, id_pdc, last_date_time_update])
    except KeyError:
        pass
# Transform in pandas dataframe. Change index and transform in date format
df = pd.read_csv(path + '/stations.csv', index_col= 'last_date_time_update',parse_dates=True)


print(df.head())

# Get hour from index into new col
df['last_update_by_hour'] = df.index.hour





















#nb_stations = dict(df['adresse_station'].value_counts())

# Get number of station by site
df['nb_charging_stations'] = df.groupby(by='adresse_station')['adresse_station'].transform('count')


# https://opendata.paris.fr/explore/dataset/belib-points-de-recharge-pour-vehicules-electriques-disponibilite-temps-reel/table/?disjunctive.statut_pdc&disjunctive.arrondissement&sort=id_pdc&dataChart=eyJxdWVyaWVzIjpbeyJjaGFydHMiOlt7InR5cGUiOiJjb2x1bW4iLCJmdW5jIjoiQ09VTlQiLCJzY2llbnRpZmljRGlzcGxheSI6dHJ1ZSwiY29sb3IiOiIjRkZDRDAwIn1dLCJ4QXhpcyI6Imxhc3RfdXBkYXRlZCIsIm1heHBvaW50cyI6IiIsInRpbWVzY2FsZSI6ImhvdXIiLCJzb3J0IjoiIiwiY29uZmlnIjp7ImRhdGFzZXQiOiJiZWxpYi1wb2ludHMtZGUtcmVjaGFyZ2UtcG91ci12ZWhpY3VsZXMtZWxlY3RyaXF1ZXMtZGlzcG9uaWJpbGl0ZS10ZW1wcy1yZWVsIiwib3B0aW9ucyI6eyJkaXNqdW5jdGl2ZS5zdGF0dXRfcGRjIjp0cnVlLCJkaXNqdW5jdGl2ZS5hcnJvbmRpc3NlbWVudCI6dHJ1ZSwic29ydCI6ImNvZGVfaW5zZWVfY29tbXVuZSJ9fX1dLCJkaXNwbGF5TGVnZW5kIjp0cnVlLCJhbGlnbk1vbnRoIjp0cnVlfQ%3D%3D&rows=999&timezone=&basemap=jawg.dark&location=12,48.86471,2.33974


#CREATION GRPH---------------------------------------------------------------------------------------------------
#MAP
mapbox_access_token = px.set_mapbox_access_token(open(path_token + "/mapbox_token.txt").read())
fig = px.scatter_mapbox(df, lat='lat', lon='long', color='statut_pdc', size='nb_charging_stations',
                        mapbox_style='carto-darkmatter', animation_group='adresse_station',opacity=0.70,
                        labels='nb_charging_stations',
                        # hover_data=[df['statut_pdc'][i] for i in range(df.shape[0])],
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=7, zoom=11.2)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
# colorscale=[
#             [0, "#F4EC15"],
#             [0.04167, "#DAF017"],
#             [0.0833, "#BBEC19"],
#             [0.125, "#9DE81B"],
#             [0.1667, "#80E41D"],
#             [0.2083, "#66E01F"],
#             [0.25, "#4CDC20"],
#             [0.292, "#34D822"],
#             [0.333, "#24D249"],
#             [0.375, "#25D042"],
#             [0.4167, "#26CC58"],
#             [0.4583, "#28C86D"],
#             [0.50, "#29C481"],
#             [0.54167, "#2AC093"],
#             [0.5833, "#2BBCA4"],
#             [1.0, "#613099"],
#             ]
# #Attribut color for inch statut for mapbox
# color = np.append(np.insert(df.index.hour, 0, 0), 3)
# print(color)
#
#
# fig = go.Figure(go.Scattermapbox(
#             lat=df["lat"],
#             lon=df["long"],
#             mode='markers',
#         marker=go.scattermapbox.Marker(dict(
#                         #colorscale=color_statut,
#                         size=9,
#                         color=np.append(np.insert(df.index.hour, 0, 0), 24),
#
#                                 )
#
#                             ),
#         text=df['statut_pdc'],
#     ))
#
# fig.update_layout(
#     autosize=True,
#     hovermode='closest',
#     showlegend=True,
#
#     mapbox=dict(
#         accesstoken="pk.eyJ1IjoiY2hyaXN0b3BoZXJnYW56YXJvbGkiLCJhIjoiY2t6bHN4Y2t6MmhkdDJwbzBoMGo4bDkyMSJ9.dHqwH6gzC1o8V24zUrTwIg",
#         bearing=0,
#
#         style="dark",
#         center=dict(
#             lat=48.86409,
#             lon=2.3437343
#
#         ),
#         pitch=0,
#         zoom=11.2,
#
#     ),
# )


#HISTOGRAM
fig_hist = px.histogram(df, x="last_update_by_hour", nbins=24)
# fig_hist = px.histogram(df, x="last_update_by_hour", y="statut_pdc", histfunc="count", nbins=24, text_auto=True)







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
