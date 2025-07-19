#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import folium
import plotly.express as px
from streamlit_folium import folium_static
from streamlit.components.v1 import components
from folium.plugins import MarkerCluster
import json

# Establecer la configuración de la página
st.set_page_config(layout="wide")

@st.cache
def load_data():
    # Cargar datos y procesar una única vez
    url = 'https://raw.githubusercontent.com/Jordan-Villanueva/Dashboard_Veredis/main/Tasa_de_Desocupacion.csv'
    data = pd.read_csv(url, encoding='latin-1', usecols=['Entidad_Federativa', 'Periodo', 'Trimestre', 'Poblacion_Economicamente_Activa', 'Sexo'])
    data = data[(data['Entidad_Federativa'] != 'Nacional')].reset_index(drop=True)
    return data

# Cargar datos
data = load_data()

@st.cache
def process_data(data, selected_year, selected_trimester):
    # Filtrar datos
    filtered_data = data.loc[(data['Periodo'] == selected_year) & (data['Trimestre'] == selected_trimester)]
    
    # Gráfico de barras
    fig = px.bar(
        filtered_data,
        x='Entidad_Federativa',
        y='Poblacion_Economicamente_Activa',
        color='Sexo',
        barmode='group',
        labels={'Poblacion_Economicamente_Activa': 'Población (millones de habitantes)'},
        color_discrete_sequence=['steelblue', 'magenta'],
        title=f'Población Económica Activa en {selected_year} - Trimestre {selected_trimester}'
    )

    # Personalizar títulos de los ejes
    fig.update_xaxes(title_text='Entidad Federativa')
    fig.update_yaxes(title_text='Población (millones de habitantes)')
    fig.update_xaxes(tickangle=-60)
    
    return filtered_data, fig

# Años y trimestres únicos
unique_years = data['Periodo'].unique()

# Diseño de la aplicación
st.title("Población Económica Activa en México")

# Dropdown para el año
selected_year = st.selectbox("Seleccionar Año:", unique_years, index=len(unique_years)-1)

# Separación vertical
st.markdown("<br>", unsafe_allow_html=True)

# Dropdown para el trimestre
if selected_year == 2023:
    trimester_options = [1, 2]
else:
    trimester_options = data['Trimestre'].unique()

selected_trimester = st.selectbox("Seleccionar Trimestre:", trimester_options, index=len(trimester_options)-1)

# Separación vertical
st.markdown("<br>", unsafe_allow_html=True)

# Procesar datos
filtered_data, fig = process_data(data, selected_year, selected_trimester)

# Usar st.plotly_chart con ancho personalizado
st.plotly_chart(fig, use_container_width=True)

# Mapa coroplético
st.title(f'Mapa Coroplético de Población Económica Activa en México en {selected_year} - Trimestre {selected_trimester}')

#poblacion total EA
filtered_data = filtered_data.groupby('Entidad_Federativa')['Poblacion_Economicamente_Activa'].sum().reset_index()

# Cargar archivo GeoJSON (asegúrate de que esté en el mismo folder que app_PEA.py)
with open("mexico_estados.geojson", "r", encoding='utf-8') as f:
    geojson_data = json.load(f)

# Convertimos a DataFrame la info del GeoJSON para poder hacer el merge
estado_list = []
for feature in geojson_data["features"]:
    estado = feature["properties"]["NOM_ENT"]
    estado_list.append(estado)
geo_df = pd.DataFrame({"NOM_ENT": estado_list})

# Normalizar nombres para hacer el merge
geo_df['NOM_ENT'] = geo_df['NOM_ENT'].replace({
    "Coahuila de Zaragoza": "Coahuila",
    "Michoacán de Ocampo": "Michoacán",
    "Veracruz de Ignacio de la Llave": "Veracruz"
})

# Merge con tus datos
merged_data = geo_df.merge(filtered_data, left_on='NOM_ENT', right_on='Entidad_Federativa', how='left')

# Create a centered container
centered_container = st.container()

# Inside the container, create the map
with centered_container:
    # Create the map of folium
    m = folium.Map(location=[23.6260333, -102.5375005], tiles='OpenStreetMap', zoom_start=5, attr="My Data attribution")

    # Your map-related code (Choropleth, MarkerCluster, etc.) goes here
    folium.Choropleth(
        geo_data=geojson_data,
        name="choropleth",
        data=merged_data,
        columns=["NOM_ENT", "Poblacion_Economicamente_Activa"],
        key_on="properties.NOM_ENT",  # Ajuste aquí
        fill_color="YlOrRd",
        fill_opacity=0.6,
        line_opacity=0.1,
        legend_name='Poblacion Economicamente Activa',
        highlight=True
    ).add_to(m)

    def add_circle_marker(row):
        geom_type = row['geometry'].geom_type
        if geom_type == 'Polygon' or geom_type == 'MultiPolygon':
            centroid = row['geometry'].centroid
            lat, lon = centroid.y, centroid.x
            popup_text = f"{row['NOM_ENT']}: {merged_data.loc[merged_data['NOM_ENT'] == row['NOM_ENT'], 'Poblacion_Economicamente_Activa'].values[0]}"
            folium.CircleMarker(
                location=[lat, lon],
                popup=popup_text,
                radius=5,
                color='blue',
                fill=True,
                fill_color='red',
                fill_opacity=0.6
            ).add_to(m)

    gdf.apply(add_circle_marker, axis=1)

    # Añadir el control
    folium.LayerControl().add_to(m)        

    folium_map_html = m._repr_html_()

    st.components.v1.html(folium_map_html, height=800) 

# Add citation
st.markdown("Creado por Jordan Ortiz. Datos obtenidos de [Datos Gubernamentales de México](https://datos.gob.mx/busca/api/3/action/package_search?q=BUSQUEDA) y [Datos CONABIO](http://geoportal.conabio.gob.mx/metadatos/doc/html/dest2019gw.html)")
