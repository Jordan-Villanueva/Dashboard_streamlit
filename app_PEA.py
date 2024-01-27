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

def st_folium(
    fig: folium.MacroElement,
    key: str | None = None,
    height: int = 700,
    width: int | None = 500,
    returned_objects: Iterable[str] | None = None,
    zoom: int | None = None,
    center: tuple[float, float] | None = None,
    feature_group_to_add: list[folium.FeatureGroup] | folium.FeatureGroup | None = None,
    return_on_hover: bool = False,
    use_container_width: bool = False,
    layer_control: folium.LayerControl | None = None,
    debug: bool = False,
):
    """Display a Folium object in Streamlit, returning data as user interacts
    with app.
    Parameters
    ----------
    fig  : folium.Map or folium.Figure
        Geospatial visualization to render
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    returned_objects: Iterable
        A list of folium objects (as keys of the returned dictionart) that will be
        returned to the user when they interact with the map. If None, all folium
        objects will be returned. This is mainly useful for when you only want your
        streamlit app to rerun under certain conditions, and not every time the user
        interacts with the map. If an object not in returned_objects changes on the map,
        the app will not rerun.
    zoom: int or None
        The zoom level of the map. If None, the zoom level will be set to the
        default zoom level of the map. NOTE that if this zoom level is changed, it
        will *not* reload the map, but simply dynamically change the zoom level.
    center: tuple(float, float) or None
        The center of the map. If None, the center will be set to the default
        center of the map. NOTE that if this center is changed, it will *not* reload
        the map, but simply dynamically change the center.
    feature_group_to_add: List[folium.FeatureGroup] or folium.FeatureGroup or None
        If you want to dynamically add features to a feature group, you can pass
        the feature group here. NOTE that if you add a feature to the map, it
        will *not* reload the map, but simply dynamically add the feature.
    return_on_hover: bool
        If True, the app will rerun when the user hovers over the map, not
        just when they click on it. This is useful if you want to dynamically
        update your app based on where the user is hovering. NOTE: This may cause
        performance issues if the app is rerunning too often.
    use_container_width: bool
        If True, set the width of the map to the width of the current container.
        This overrides the `width` parameter.
    layer_control: folium.LayerControl or None
        If you want to have layer control for dynamically added layers, you can
        pass the layer control here.
    debug: bool
        If True, print out the html and javascript code used to render the map with
        st.code
    Returns
    -------
    dict
        Selected data from Folium/leaflet.js interactions in browser
    """
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.

    if use_container_width:
        width = None

    folium_map: folium.Map = fig  # type: ignore

    # handle the case where you pass in a figure rather than a map
    # this assumes that a map is the first child
    if not (isinstance(fig, folium.Map) or isinstance(fig, folium.plugins.DualMap)):
        folium_map = list(fig._children.values())[0]

    folium_map.render()

    leaflet = _get_map_string(folium_map)  # type: ignore

    html = _get_siblings(folium_map)

    m_id = get_full_id(folium_map)


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

# Ruta a los archivos shapefile
shapefile_path = 'dest2019gw/dest2019gw.shp'

# Leer el archivo shapefile
gdf = gpd.read_file(shapefile_path, encoding='utf-8')
gdf['NOM_ENT'][4] = 'Coahuila'
gdf['NOM_ENT'][15] = 'Michoacán'
gdf['NOM_ENT'][29] = 'Veracruz'

# Supongamos que la columna 'Entidad_Federativa' es la clave
merged_data = gdf.merge(filtered_data, left_on='NOM_ENT', right_on='Entidad_Federativa', how='left')

# Simplificar la geometría
gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.005)

# Create a centered container
centered_container = st.container()

# Inside the container, create the map
with centered_container:
    # Create the map of folium
    m = folium.Map(location=[23.6260333, -102.5375005], tiles='OpenStreetMap', zoom_start=5, attr="My Data attribution")

    # Your map-related code (Choropleth, MarkerCluster, etc.) goes here
    folium.Choropleth(
        geo_data=gdf,
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
    st_folium(
    m,
    center=st.session_state["center"],
    zoom=st.session_state["zoom"],
    key="new",
    height=400,
    width=700)
    
    # Display the map using folium_static
    # folium_static(m, width=800, height=600)
    
# Add citation
st.markdown("Datos obtenidos de [Datos Gubernamentales de México](https://datos.gob.mx/busca/api/3/action/package_search?q=BUSQUEDA) y [Datos CONABIO](http://geoportal.conabio.gob.mx/metadatos/doc/html/dest2019gw.html)")
