#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 11:52:29 2021

@author: laurayarce
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(layout="wide")# Utilizar la página completa en lugar de una columna central estrecha

# Título principal, h1 denota el estilo del título 1
st.markdown("<h1 style='text-align: center; color: #3C9AD0;'>Histórico de disparos en Nueva York 🗽 🔫 </h1>", unsafe_allow_html=True)

# Función para importar datos
@st.cache(persist=True) # Código para que quede almacenada la información en el cache
def load_data(url):
    df = pd.read_csv(url) # leer datos
    df['OCCUR_DATE'] = pd.to_datetime(df['OCCUR_DATE']) # convertir fecha a formato fecha
    df['OCCUR_TIME'] = pd.to_datetime(df['OCCUR_TIME'], format='%H:%M:%S') # convertir hora a formato fecha
    df['YEAR'] = df['OCCUR_DATE'].dt.year # sacar columna con año
    df['HOUR'] = df['OCCUR_TIME'].dt.hour # sacar columna con hora
    df['YEARMONTH'] = df['OCCUR_DATE'].dt.strftime('%y%m') # sacar columna con año/mes
    df.columns = df.columns.map(str.lower) # convertir columnas a minúscula
    
    return df

# Aplicar función
df = load_data('NYPD_Shooting_Incident_Data__Historic_.csv')

#---------------------------------------------------------------------

# Dividir el layout en cuatro partes
c1, c2= st.beta_columns((1,1)) # Entre paréntesis se indica el tamaño de las columnas


# Hacer código de la primera columna (Mapa sencillo):
c1.markdown("<h3 style='text-align: center; color: black;'> ¿Dónde han ocurrido disparos en Nueva York? </h3>", unsafe_allow_html=True)
year = c1.slider('Año en el que se presento el suceso', df['year'].min(), df['year'].max()) # Crear variable que me almacene el año seleccionado
c1.map(df[df['year']==year][['latitude', 'longitude']].dropna()) # Generar mapa

  
# Hacer código de la segunda columna:
c2.markdown("<h3 style='text-align: center; color: black;'> ¿A qué horas ocurren disparos en Nueva York? </h3>", unsafe_allow_html=True)
hora = c2.slider('Hora en la que se presento el suceso', df['hour'].min(), df['hour'].max()) # Crear variable que me almacene la hora seleccionada
df2 = df[df['hour']==hora] # Filtrar DataFrame


c2.write(pdk.Deck( # Código para crear el mapa
    
    # Set up del mapa
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state={
        'latitude' : df['latitude'].mean(),
        'longitude': df['longitude'].mean(),
        'zoom' : 9.5,
        'pitch': 50
        },
    
    # Capa con información
    layers = [pdk.Layer(
        'HexagonLayer',
        data = df2[['incident_key','latitude','longitude']],
        get_position = ['longitude','latitude'],
        radius = 100,
        extruded = True,
        elevation_scale = 4,
        elevation_range = [0,1000])]
    ))

#---------------------------------------------------------------------

# Título de la siguiente sección
st.markdown("<h3 style='text-align: center; color: black;'> ¿Cómo ha sido la evolución de disparos por barrio? </h3>", unsafe_allow_html=True)

# Organizar DataFrame
df2 = df.groupby(['yearmonth','boro'])[['incident_key']].count().reset_index().rename(columns = {'incident_key':'disparos'})

# Generar gráfica
fig = px.line(df2, x='yearmonth', y='disparos', color = 'boro', width=1100, height=450)

# Editar gráfica
fig.update_layout(
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template = 'simple_white',
        xaxis_title="<b>Año<b>",
        yaxis_title='<b>Cantidad de incidentes<b>',
        legend_title_text='',
        
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.8))

# Enviar gráfica a streamlit
st.plotly_chart(fig)

#---------------------------------------------------------------------

# Dividir siguiente sección
c4, c5, c6, c7= st.beta_columns((1,1,1,1))

################ ---- Primera Gráfica

# Definir título
c4.markdown("<h3 style='text-align: center; color: black;'> ¿Qué edad tienen los atacantes? </h3>", unsafe_allow_html=True)

# Organizar DataFrame
df2 = df.groupby(['perp_age_group'])[['incident_key']].count().reset_index().rename(columns = {'incident_key':'disparos'})

# Editar categorías mal escritas
df2['perp_age_group'] = df2['perp_age_group'].replace({'940':'UNKNOWN',
                              '224':'UNKNOWN','1020':'UNKNOWN'})

# Cambiar UNKNOWN por un nombre más corto
df2['perp_age_group'] = df2['perp_age_group'].replace({
                              'UNKNOWN': 'N/A'})

# Crear categoría para organizar el orden de las edades
df2['perp_age_group2'] = df2['perp_age_group'].replace({'<18':'1',
                              '18-24':'2',
                              '25.44':'3',
                              '45-64':'4',
                              '65+':'5',
                              'UNKNOWN': '6'})
# Aplicar orden al DataFrame
df2= df2.sort_values('perp_age_group2',ascending = False)

# Hacer gráfica
fig = px.bar(df2, x="disparos", y="perp_age_group", orientation='h', width=340,  height=310)
fig.update_layout(xaxis_title="<b>Atacante<b>",
                  yaxis_title="<b>Edades<b>", template = 'simple_white',
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)')

# Enviar gráfica a streamlit
c4.plotly_chart(fig)

################ ---- Segunda Gráfica


# Definir título
c5.markdown("<h3 style='text-align: center; color: black;'> ¿Qué edad tienen los víctimas? </h3>", unsafe_allow_html=True)

# Organizar DataFrame
df2 = df.groupby(['vic_age_group'])[['incident_key']].count().reset_index().rename(columns = {'incident_key':'disparos'})

# Crear categoría para organizar el orden de las edades
df2['vic_age_group2'] = df2['vic_age_group'].replace({'<18':'1',
                              '18-24':'2',
                              '25.44':'3',
                              '45-64':'4',
                              '65+':'5',
                              'UNKNOWN': '6'})

# Cambiar UNKNOWN por un nombre más corto
df2['vic_age_group'] = df2['vic_age_group'].replace({
                              'UNKNOWN': 'N/A'})

# Aplicar orden al DataFrame
df2= df2.sort_values('vic_age_group2',ascending = False)

# Hacer gráfica
fig = px.bar(df2, x="disparos", y="vic_age_group", orientation='h', width=340,  height=310)
fig.update_layout(xaxis_title="<b>Víctimas<b>",
                  yaxis_title="<b><b>", template = 'simple_white',
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)')

# Enviar gráfica a streamlit
c5.plotly_chart(fig)

################ ---- Tercera Gráfica

# Definir título
c6.markdown("<h3 style='text-align: center; color: Black;'> ¿Cuál es el sexo del atacante? </h3>", unsafe_allow_html=True)

# Organizar DataFrame
df2 = df.groupby('perp_sex')[['incident_key']].count().reset_index().sort_values('incident_key', ascending = False)

# Hacer gráfica
fig = px.pie(df2, values = 'incident_key', names="perp_sex",
             width=300, height=300)
fig.update_layout(template = 'simple_white',
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  legend=dict(orientation="h",
                              yanchor="bottom",
                              y=-0.4,
                              xanchor="center",
                              x=0.5))

# Enviar gráfica a streamlit
c6.plotly_chart(fig)

################ ---- Cuarta Gráfica

# Definir título
c7.markdown("<h3 style='text-align: center; color: Black;'> ¿Cuál es el sexo de la víctima? </h3>", unsafe_allow_html=True)

# Organizar DataFrame
df2 = df.groupby('vic_sex')[['incident_key']].count().reset_index().sort_values('incident_key', ascending = False)

# Hacer gráfica
fig = px.pie(df2, values = 'incident_key', names="vic_sex",
             width=300, height=300)
fig.update_layout(template = 'simple_white',
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  legend=dict(orientation="h",
                              yanchor="bottom",
                              y=-0.4,
                              xanchor="center",
                              x=0.5))

# Enviar gráfica a streamlit
c7.plotly_chart(fig)


#---------------------------------------------------------------------

# Definir título
st.markdown("<h3 style='text-align: center; color: Black;'> Evolución de disparos por año en las horas con más y menos sucesos </h3>", unsafe_allow_html=True)

# Organizar DataFrame
df2 = df[df['hour'].isin([23,9])].groupby(['year','hour'])[['incident_key']].sum().sort_values('incident_key', ascending = False).reset_index() 
df2['hour'] = df2['hour'].astype('category')


# Hacer gráfica
fig = px.bar(df2, x='year', y='incident_key', color ='hour', barmode='group', width=1150, height=450)
fig.update_layout(
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template = 'simple_white',
        legend_title_text = 'Hora',
        xaxis_title="<b>Año<b>",
        yaxis_title="<b>Cantidad de incidentes<b>")

# Enviar gráfica a streamlit
st.plotly_chart(fig)

#---------------------------------------------------------------------

# Hacer un checkbox
if st.checkbox('Obtener datos por fecha y barrio', False):
    
    # Código para generar el DataFrame
    df2 = df.groupby(['occur_date','boro'])[['incident_key']].count().reset_index().rename(columns ={'boro':'Barrio','occur_date':'Fecha','incident_key':'Cantidad'})
    df2['Fecha'] = df2['Fecha'].dt.date
    
    # Código para convertir el DataFrame en una tabla plotly resumen
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df2.columns),
        fill_color='lightgrey',
        line_color='darkslategray'),
        cells=dict(values=[df2.Fecha, df2.Barrio, df2.Cantidad],fill_color='white',line_color='lightgrey'))
       ])
    fig.update_layout(width=500, height=450)

# Enviar tabla a streamlit
    st.write(fig)
