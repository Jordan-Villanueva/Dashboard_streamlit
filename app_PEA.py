# Esta es la version que integra el diagrama de barras con el mapa coropletico en streamlit, relacionando la poblacion economicamente activa.

import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_folium import folium_static

# Establecer la configuración de la página
st.set_page_config(layout="wide")

# Cargar datos
url = 'https://raw.githubusercontent.com/Jordan-Villanueva/Dashboard_Veredis/main/Tasa_de_Desocupacion.csv'
data = pd.read_csv(url, encoding='latin-1')
data = data[(data['Entidad_Federativa'] != 'Nacional')].reset_index(drop=True)
data = data.drop(columns=['Unnamed: 7', 'Unnamed: 8'])

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

# Filtrar datos
filtered_data = data[(data['Periodo'] == selected_year) & (data['Trimestre'] == selected_trimester)]

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

# Usar st.plotly_chart con ancho personalizado
st.plotly_chart(fig, use_container_width=True)

# Mapa coroplético
st.title("Mapa Coroplético de Población Económica Activa en México")

# Ruta a los archivos shapefile
shapefile_path = 'dest2019gw/dest2019gw.shp'

# Leer el archivo shapefile
gdf = gpd.read_file(shapefile_path, encoding='utf-8')
gdf['NOM_ENT'][4] = 'Coahuila'
gdf['NOM_ENT'][15] = 'Michoacán'
gdf['NOM_ENT'][29] = 'Veracruz'

# Supongamos que la columna 'Entidad_Federativa' es la clave
merged_data = gdf.merge(filtered_data, left_on='NOM_ENT', right_on='Entidad_Federativa', how='left')

# Crear una nueva columna con la información deseada para el tooltip
merged_data['Tooltip'] = merged_data.apply(lambda row: f"{row['NOM_ENT']}: {row['Poblacion_Economicamente_Activa']}", axis=1)

m = folium.Map(location=[23.6260333, -102.5375005], tiles='OpenStreetMap', name='Light Map', zoom_start=6, attr="My Data attribution")

# Añadir la capa coroplética con GeoJsonTooltip
folium.Choropleth(
    geo_data=merged_data,
    name="choropleth",
    data=merged_data,
    columns=["NOM_ENT", "Poblacion_Economicamente_Activa"],
    key_on="feature.properties.NOM_ENT",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.1,
    legend_name='Poblacion_Economicamente_Activa',
    highlight=True,  # Para resaltar las entidades al pasar el cursor
    tooltip=folium.features.GeoJsonTooltip(fields=['Tooltip'], labels=False)
).add_to(m)

# Añadir el control de capas
folium.LayerControl().add_to(m)

# Desplegar el mapa
folium_static(m, width=1600, height=950)


# Add citation
st.markdown("Datos obtenidos de [Datos Gubernamentales de México](https://datos.gob.mx/busca/api/3/action/package_search?q=BUSQUEDA) y [Datos CONABIO](http://geoportal.conabio.gob.mx/metadatos/doc/html/dest2019gw.html)")
