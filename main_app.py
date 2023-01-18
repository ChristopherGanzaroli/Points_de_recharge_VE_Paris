import sqlite3
import pandas as pd
from collections import defaultdict
import plotly.express as px

path = r"C:/Users/ganza/OneDrive/Bureau/projets_data_engineering/ve_stations_paris\app/Points_de_recharge_VE_Paris/"
def get_data() :
    conn = sqlite3.connect(r"C:\Users\ganza\OneDrive\Bureau\projets_data_engineering\ve_stations_paris\database\paris_ve.db")
    df = pd.read_sql_query("SELECT time,adress,district,status,post_code,lat,long,id_pdc FROM paris_station_act ORDER BY time", conn)
    conn.close()
    return df
df = get_data()

#################################################################################################
# FEATURE ENGINEERING
#################################################################################################

df['nb_charging_stations'] = df.groupby(by='adress')['adress'].transform('count')


def statut_count(df):

    if  df.status == "Occupé (en charge)" :
        return 1
    else:
        None

df["occupation (1=yes, 0=no)"] = df.apply(statut_count, axis=1)

df["occupation (1=yes, 0=no)"] = df.groupby(by="adress")["occupation (1=yes, 0=no)"].transform('count')

d = defaultdict(list)
for k,v in zip(df.post_code,df["occupation (1=yes, 0=no)"]):
    if v == 1:
        d[k].append(v)

for k,v in d.items():
    d[k] = sum(v)
df_occupation_by_dept = pd.DataFrame(d.items(), columns=['dept', 'nb station anvailable'])

#dictionnaire contenant le nombre de bornes de recharge par arrondissements
d= defaultdict(list)
for k,v in zip(df.post_code,df['nb_charging_stations']):
    d[k].append(v)

for k,v in d.items():
    d[k] = sum(v)
df_nb_charging_station_by_dept = pd.DataFrame(d.items(), columns=['dept', 'nb of charging station'])
df_nb_charging_station_by_dept

#Création du dataframe mesurant le taux d'occupation pour chaque arrondissement
df_nb_charging_station_by_dept['tx_occupation_by_dept'] = ((df_occupation_by_dept['nb station anvailable']/df_nb_charging_station_by_dept['nb of charging station'])*100).round(2)


####################################################################################################################
# APP
####################################################################################################################

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

############################### HISTOGRAM ###############################
'''
On cherche ici à afficher l'occupation des bornes de recharge.
On va donc créer une nouvelle colonnes afin d'extraire si "oui" ou non la station est disponible.
si "oui", on récupère l'heure

'''



fig_hist = px.bar(df_nb_charging_station_by_dept,
                  x=df_nb_charging_station_by_dept["dept"].astype(str),
                  y=df_nb_charging_station_by_dept['tx_occupation_by_dept'],
                  text_auto=True,
                  color="dept",
                  labels={'x':'Départements', 'y':"Taux d'occupation en %"})

fig_hist.update_coloraxes(colorscale=colorscale)
fig_hist.update_layout(bargap=0.01,showlegend=False)

fig_hist2 = px.bar(df_nb_charging_station_by_dept,
                   x=df_nb_charging_station_by_dept["dept"].astype(str),
                   y=df_nb_charging_station_by_dept['tx_occupation_by_dept'],
                   text_auto=True,
                   color="dept",
                   labels={'x':'Départements', 'y':"Taux d'occupation en %"})

fig_hist2.update_coloraxes(colorscale=colorscale)
fig_hist2.update_layout(bargap=0.01,showlegend=False)

# nb_disponibility_station_by_hours = []
# for a,b in zip(df.last_update_by_hour, df["occupation (1=yes, 0=no)"]):
#     if b == 1:
#         nb_disponibility_station_by_hours.append(a)
# hours_hist = ([i for i in df.last_update_by_hour] + [i for i in range(0,24) if i not in nb_disponibility_station_by_hours])

# fig_hist3 = px.histogram(x=hours_hist,text_auto=True)
# #Espacer les bars
# fig_hist3.update_layout(bargap=0.01,showlegend = False)
###################### PROBLEMES ######################
#Pourquoi y a-t'il tant d'occupation à 2h ?
#print(hours_hist[hours_hist == 2])


# CREATION DA L APPLICATION DASH
import dash
from dash import Dash, html, dcc, dash_table
import plotly.express as px
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_table as dt



app = Dash(__name__)
########################################################################################################################
# UPDATE
########################################################################################################################

app_colors = {
    'background': '#343332',
    'text': '#FFFFFF'
}


fig_hist.update_layout(
    plot_bgcolor=app_colors['background'],
    paper_bgcolor=app_colors['background'],
    font_color=app_colors['text'],
    margin={"r":0,"t":0,"l":0}
)
fig_hist2.update_layout(
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
                                          #Elements in left component
                                          html.Div(
                                              className='elt_in_left_components',
                                              children=[
                                                  html.H1(
                                                      "Carte des bornes de recharge à Paris",
                                                      style={
                                                          'textAlign': 'center',
                                                          'color': app_colors['text'],
                                                          'margin': '0%'
                                                      }
                                                  ),
                                                  html.Div(
                                                      className='DD_div',
                                                      children=[
                                                          #html.Label(['Arrondissement'], style={'font-weight':'bold','font-size': '1rem', 'color':'white'}),
                                                          html.Br(),
                                                          dcc.Dropdown( #Dropdown dept
                                                              id='DD_dept_input',
                                                              options=
                                                              [dict(label=x, value=x)
                                                               for x in df['post_code'].unique()],
                                                              placeholder="Selectionnez un arrondissement",
                                                              style = {
                                                                  # 'color': 'white',
                                                                  'backgroundColor': 'transparent',
                                                              }

                                                          ),
                                                          #html.Label(['Adresse'], style={'font-weight':'bold','font-size': '1rem', 'color':'white'}),
                                                          dcc.Dropdown( #Dropdown adresse
                                                              id='DD_adress_input',
                                                              options=
                                                              [dict(label=x, value=x)
                                                               for x in df['adress'].unique()],
                                                              placeholder="Selectionnez une adresse",
                                                              style = {
                                                                  'backgroundColor': 'transparent',

                                                              }


                                                          ),
                                                      ]
                                                  ),

                                                  dt.DataTable(
                                                      id='output_datatable',
                                                      columns=[
                                                          {'name': 'post_code' ,'id' : 'post_code', 'type' : 'numeric'},
                                                          {'name': 'adress' ,'id' : 'adress', 'type' : 'text'},
                                                          {'name': 'status' ,'id' : 'status', 'type' : 'text'},
                                                          {'name': 'id_pdc' ,'id' : 'id_pdc', 'type' : 'text'},
                                                      ],
                                                      data=df.to_dict('records'),
                                                      page_size=6,
                                                      style_as_list_view=True,
                                                      style_data={
                                                          #'width':'50px',
                                                          'overflow':'hidden',
                                                          'textOverflow' : 'ellipsis',
                                                          'color': 'white',
                                                          'backgroundColor': 'transparent',
                                                          'whiteSpace': 'normal',
                                                          'width': 'auto',

                                                      },
                                                      style_table={
                                                          'overflowX': 'auto'
                                                      },
                                                      style_cell={
                                                          'overflow': 'hidden',
                                                          'textOverflow': 'ellipsis',
                                                          'textAlign': 'left',

                                                      },
                                                      style_header={
                                                          'backgroundColor': 'rgb(50, 50, 50)',
                                                          'color': 'white',
                                                          'fontWeight': 'bold',
                                                          'border': '1px solid black'
                                                      },
                                                      style_cell_conditional=[
                                                          {'if': {'column_id': 'post_code'},
                                                           'width': '5%'}
                                                      ]

                                                  ),


                                              ]#end children

                                          )

                                      ]
                                  ),

                                  #Map hist
                                  html.Div(className='map_hist',
                                           children=[
                                               html.Div(

                                                   dcc.Graph(
                                                       className='map',
                                                       id="map_output",

                                                       #figure=fig

                                                   )
                                               ),
                                               html.Div(

                                                   dcc.Graph(
                                                       className='hist',
                                                       id="hist1_output",
                                                       figure=fig_hist

                                                   )


                                               ),
                                               html.Div(

                                                   dcc.Graph(
                                                       className='hist',
                                                       id='hist2_output',
                                                       figure=fig_hist2

                                                   )


                                               )
                                           ]
                                           )


                              ])

                      ]#end children

                      )

########################################################################################################################
# CALLBACK
########################################################################################################################

"""
Avec "CALLBACK", nous allons maintenant connecter nos différents composents.
"""

############################### MAP TABLE ###############################

@app.callback(
    Output('map_output', 'figure'),

    Input('DD_dept_input',"value"),
    Input('DD_adress_input',"value")
)
def update_map_map(DD_dept_input,DD_adress_input) :
    map_feltred = df.copy()

    # if  not DD_dept_input :
    #     raise PreventUpdate
    # else :
    if DD_dept_input :
        map_feltred = map_feltred[map_feltred.post_code == DD_dept_input]



    elif DD_adress_input:
        map_feltred = map_feltred[(map_feltred.adress==DD_adress_input) & (map_feltred.status=='Occupé (en charge)')]


    ######################################## MAP ###############################################
    mapbox_access_token = px.set_mapbox_access_token(open(path + "mapbox_token.txt").read())
    fig = px.scatter_mapbox(map_feltred, lat='lat', lon='long', size=((map_feltred["occupation (1=yes, 0=no)"]/map_feltred["nb_charging_stations"])*100).round(2),
                            labels={'y':'Départements'},#labels='nb_charging_stations'
                            mapbox_style='carto-darkmatter', animation_group='adress',opacity=0.20,
                            hover_data=['adress','nb_charging_stations'], color="post_code",

                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=12, zoom=11.2)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0,})

    fig.update_layout(coloraxis_showscale=False)
    #fig.update_traces(hovertemplate=None)
    fig.update_layout(
        plot_bgcolor=app_colors['background'],
        paper_bgcolor=app_colors['background'],
        font_color=app_colors['text'],
        margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_coloraxes(colorscale=colorscale)

    return fig


@app.callback(

    Output('output_datatable', 'data'),
    Input('DD_dept_input',"value"),
    Input('DD_adress_input',"value")
)
def update_map_map(DD_dept_input,DD_adress_input) :
    df_feltred = df.copy()

    if   DD_dept_input :

        table_feltred = df_feltred[(df_feltred.post_code==DD_dept_input) ]

    if DD_adress_input:
        table_feltred = df_feltred[(df_feltred.adress==DD_adress_input)]

    return table_feltred.to_dict('records')


app.config.suppress_callback_exceptions = True

app.run_server(debug=True, use_reloader=True)