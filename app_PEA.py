#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import plotly.express as px
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# Establecer la configuración de la página
st.set_page_config(layout="wide")

@st.cache
def load_data():
    # Cargar datos y procesar una única vez
    url = 'https://raw.githubusercontent.com/Jordan-Villanueva/Dashboard_Veredis/main/Tasa_de_Desocupacion.csv'
    data = pd.read_csv(url, encoding='latin-1', usecols=['Entidad_Federativa', 'Periodo', 'Trimestre', 'Poblacion_Economicamente_Activa', 'Sexo'])
    data = data[(data['Entidad_Federativa'] != 'Nacional')].reset_index(drop=True)
    return data

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


# Cargar datos
data = load_data()

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
st.title("Mapa Coroplético de Población Económica Activa en México")

#poblacion total EA
filtered_data = filtered_data.groupby('Entidad_Federativa')['Poblacion_Economicamente_Activa'].sum().reset_index()

# Ruta a los archivos shapefile
shapefile_path = 'dest2019gw/dest2019gw.shp'

# Leer el archivo shapefile
gdf = gpd.read_file(shapefile_path, encoding='utf-8')
gdf['NOM_ENT'][4] = 'Coahuila'
gdf['NOM_ENT'][15] = 'Michoacán'
gdf['NOM_ENT'][29] = 'Veracruz'

# Supongamos que la columna 'Entidad_Federativa' es la clave
merged_data = gdf.merge(filtered_data, left_on='NOM_ENT', right_on='Entidad_Federativa', how='left')

# Crear el mapa de folium
m = folium.Map(location=[23.6260333, -102.5375005], tiles='OpenStreetMap', name='Light Map', zoom_start=5, attr="My Data attribution")

# Añadir la capa coroplética con GeoJsonTooltip
folium.Choropleth(
    geo_data=merged_data,
    name="choropleth",
    data=merged_data,
    columns=["NOM_ENT", "Poblacion_Economicamente_Activa"],
    key_on="properties.NOM_ENT",  # Ajuste aquí
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.1,
    legend_name='Poblacion Economicamente Activa',
    highlight=True,
    tooltip=folium.GeoJsonTooltip(fields=['NOM_ENT', 'Poblacion_Economicamente_Activa'], aliases=['Entidad Federativa', 'Población Total'], localize=True, sticky=False)
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

# Desplegar el mapa
folium_static(m, width=1600, height=950)

# Add citation
st.markdown("Datos obtenidos de [Datos Gubernamentales de México](https://datos.gob.mx/busca/api/3/action/package_search?q=BUSQUEDA) y [Datos CONABIO](http://geoportal.conabio.gob.mx/metadatos/doc/html/dest2019gw.html)")
