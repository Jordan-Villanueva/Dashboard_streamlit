import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
url = 'https://raw.githubusercontent.com/Jordan-Villanueva/Dashboard_Veredis/main/Tasa_de_Desocupacion.csv'
data = pd.read_csv(url, encoding='latin-1')
data = data[(data['Entidad_Federativa'] != 'Nacional')].reset_index(drop=True)
data = data.drop(columns=['Unnamed: 7', 'Unnamed: 8'])

# Unique years and trimesters
unique_years = data['Periodo'].unique()

# Title
st.title("Población Económica Activa en México")

# Select Year
selected_year = st.selectbox("Seleccionar Año:", unique_years, index=len(unique_years)-1)

# Select Trimester
if selected_year == 2023:
    trimester_options = [1, 2]
    selected_trimester = st.selectbox("Seleccionar Trimestre:", trimester_options)
else:
    trimester_options = data['Trimestre'].unique()
    selected_trimester = st.selectbox("Seleccionar Trimestre:", trimester_options, index=len(trimester_options)-1)

# Filter data
filtered_data = data[(data['Periodo'] == selected_year) & (data['Trimestre'] == selected_trimester)]

# Bar Chart
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

# Customize axes titles
fig.update_xaxes(title_text='Entidad Federativa')
fig.update_yaxes(title_text='Población (millones de habitantes)')
fig.update_xaxes(tickangle=-60)

# Display Bar Chart
st.plotly_chart(fig)
