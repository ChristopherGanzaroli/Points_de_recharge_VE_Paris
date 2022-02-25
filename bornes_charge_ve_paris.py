import requests
import json
import csv
import pandas as pd
from datetime import datetime
import datetime
import plotly.express as px
from pandas.tseries.frequencies import to_offset
import plotly.graph_objects as go

# In[2]:


pd.set_option('display.max_rows', 10)

# In[3]:


r = requests.get(
    "https://opendata.paris.fr/api/records/1.0/search/?dataset=belib-points-de-recharge-pour-vehicules-electriques-disponibilite-temps-reel&q=&rows=9999&sort=code_insee_commune&facet=statut_pdc&facet=last_updated&facet=arrondissement")
data = r.json()
# print(data)


# In[4]:


json.dumps(data, indent=4, sort_keys=False)

# In[5]:


# pwd


# In[6]:


path = "/Users/ganza/OneDrive/Bureau/Projet_prerso/python/points_recharche_VE_open_data/data"
path2 = "/Users/ganza/OneDrive/Bureau/Projet_prerso/python/points_recharche_VE_open_data"

# In[7]:


with open(path + '/data.json', 'w') as json_file:
    json.dump(data, json_file, indent=4, sort_keys=False)

# In[8]:


sites = data['records']
with open(path + '/stations.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(
        ['adresse_station', 'arrondissement', 'statut_pdc', 'code_insee_commune', 'coordonneesxy', 'lat', 'long',
         'id_pdc', 'last_date_time_update', 'last_date_update', 'last_time_update'])
    # try:
    for elt in sites:
        adress = elt["fields"]["adresse_station"]
        # print(adress)
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
        last_date_update = last_date_time_update.date()
        last_time_update = last_date_time_update.time()

        writer.writerow([adress, arrondissement, statut, cp, lat_long, lat, long, id_pdc,last_date_time_update,last_date_update,last_time_update])

# In[9]:


df = pd.read_csv(path + '/stations.csv')

print(df.head())

#Transform in PD timeserie
# print(pd.to_datetime(df['last_date_time_update']))
# print(pd.to_datetime(df['last_date_update']))
# print(pd.to_datetime(df['last_time_update']))



# for i in df['adresse_station']:
#     if i == '62 Jean-Jacques Rousseau 75001 Paris' :
#         print(i)


# In[11]:


nb_stations = dict(df['adresse_station'].value_counts())

# In[12]:


df['nb_charging_stations'] = df.groupby(by='adresse_station')['adresse_station'].transform('count')

# print(df.head())


# https://opendata.paris.fr/explore/dataset/belib-points-de-recharge-pour-vehicules-electriques-disponibilite-temps-reel/table/?disjunctive.statut_pdc&disjunctive.arrondissement&sort=id_pdc&dataChart=eyJxdWVyaWVzIjpbeyJjaGFydHMiOlt7InR5cGUiOiJjb2x1bW4iLCJmdW5jIjoiQ09VTlQiLCJzY2llbnRpZmljRGlzcGxheSI6dHJ1ZSwiY29sb3IiOiIjRkZDRDAwIn1dLCJ4QXhpcyI6Imxhc3RfdXBkYXRlZCIsIm1heHBvaW50cyI6IiIsInRpbWVzY2FsZSI6ImhvdXIiLCJzb3J0IjoiIiwiY29uZmlnIjp7ImRhdGFzZXQiOiJiZWxpYi1wb2ludHMtZGUtcmVjaGFyZ2UtcG91ci12ZWhpY3VsZXMtZWxlY3RyaXF1ZXMtZGlzcG9uaWJpbGl0ZS10ZW1wcy1yZWVsIiwib3B0aW9ucyI6eyJkaXNqdW5jdGl2ZS5zdGF0dXRfcGRjIjp0cnVlLCJkaXNqdW5jdGl2ZS5hcnJvbmRpc3NlbWVudCI6dHJ1ZSwic29ydCI6ImNvZGVfaW5zZWVfY29tbXVuZSJ9fX1dLCJkaXNwbGF5TGVnZW5kIjp0cnVlLCJhbGlnbk1vbnRoIjp0cnVlfQ%3D%3D&rows=999&timezone=&basemap=jawg.dark&location=12,48.86471,2.33974


# In[34]:

#CREATION GRPH---------------------------------------------------------------------------------------------------
#MAP
px.set_mapbox_access_token(open(path2 + "/mapbox_token.txt").read())
fig = px.scatter_mapbox(df, lat='lat', lon='long', color='statut_pdc', size='nb_charging_stations',
                        mapbox_style='carto-darkmatter', animation_group='adresse_station',height=500,
                        labels='nb_charging_stations',
                        # hover_data=[df['statut_pdc'][i] for i in range(df.shape[0])],
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=10, zoom=11.2)
fig.update_layout(margin={"r":0,"t":0,"l":50,"b":0})
# fig.show()



#HISTOGRAM

print(df['last_time_update'].groupby(pd.Grouper(freq='60Min', base=30, label='right')).first())
print(type(df['last_time_update'][0]))
fig_hist = px.histogram(df, x="last_time_update", nbins=23)
#fig_hist.show()





#test pour app dash
import plotly.graph_objects as go
fig2 = go.Figure(
    data=[go.Bar(y=[2, 1, 3])],
    layout_title_text="A Figure Displaying Itself"
)














# CREATION DA L APPLICATION DASH
from dash import Dash, html, dcc
import plotly.express as px
from dash.dependencies import Input, Output

# Definir les paramettres du dropdown

dropdow_map_options = [dict(label=x, value=x)
              for x in df['code_insee_commune'].unique()]

app = Dash(__name__)

app_colors = {
    'background': '#0B0B0B',
    'text': '#FFFFFF'
}

fig.update_layout(
    plot_bgcolor=app_colors['background'],
    paper_bgcolor=app_colors['background'],
    font_color=app_colors['text']
    #margin={"r":0,"t":0,"l":0,"b":0}
)

app.title = "Stations de recharge Paris"

app.layout = html.Div(style={'background-color': app_colors['background'],
                             'paper_bgcolor' :app_colors['background'],
                             'margin': '0px'},
                      className= "content",
                        children=[
                          html.H1(
                              "Carte des bornes de recharge à Paris",
                              style={
                                  'textAlign': 'center',
                                  'color': app_colors['text'],
                                  'margin': '2%'
                              }
                          ),


                        #Map check list 1
                          html.Div(
                              className='map_chexLiest',
                              children=[

                                  html.Div(className="ddropdown_map_cp",
                                    children=[
                                        dcc.Dropdown(id='DDMap',
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
                        #Map
                                  html.Div(className='map',
                                      children=[
                                        dcc.Graph(
                                            figure=fig
                              ),
                                          dcc.Graph(
                                            figure=fig_hist
                              )
                        ]
                    ),




                        ]



                ),



            ]#end children

        )


app.run_server(debug=True, use_reloader=True)

