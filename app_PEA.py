import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd

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

# Gráfico
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

st.title("Mapa Coroplético de Población Económica Activa en México")

# Descargar el archivo zip del shapefile
shapefile_zip_url = "https://github.com/Jordan-Villanueva/Dashboard_streamlit/blob/main/Mexico_Estados.zip"
response = requests.get(shapefile_zip_url)
with zipfile.ZipFile(BytesIO(response.content), 'r') as zip_ref:
    zip_ref.extractall('shapefile_folder')

# Cargar el shapefile
gdf = gpd.read_file('shapefile_folder/Mexico_Estados.shp')

# Fusionar datos espaciales con datos de población económica activa
merged_data = gdf.merge(filtered_data, left_on='ID', right_on='ID', how='left')

# Crear el mapa coroplético
fig_mapa = px.choropleth(
    merged_data,
    geojson=merged_data.geometry,
    locations=merged_data.index,
    color='Poblacion_Economicamente_Activa',
    color_continuous_scale="Viridis",
    labels={'Poblacion_Economicamente_Activa': 'Población (millones de habitantes)'},
    title=f'Mapa Coroplético de Población Económica Activa en {selected_year} - Trimestre {selected_trimester}'
)

# Usar st.plotly_chart con ancho personalizado
st.plotly_chart(fig_mapa, use_container_width=True)

# Add citation
st.markdown("Datos obtenidos de [Datos Gubernamentales de México](https://datos.gob.mx/busca/api/3/action/package_search?q=BUSQUEDA)")
