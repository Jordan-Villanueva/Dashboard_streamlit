import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
url = 'https://raw.githubusercontent.com/Jordan-Villanueva/Dashboard_Veredis/main/Tasa_de_Desocupacion.csv'
data = pd.read_csv(url, encoding='latin-1')
data = data[(data['Entidad_Federativa'] != 'Nacional')].reset_index(drop=True)
data = data.drop(columns=['Unnamed: 7', 'Unnamed: 8'])

# Unique years and trimesters
unique_years = data['Periodo'].unique()

# Streamlit app layout
st.title("Población Económica Activa en México")

# Dropdowns for year and trimester selection
selected_year = st.selectbox("Seleccionar Año:", unique_years, index=len(unique_years)-1)

if selected_year == 2023:
    selected_trimester = st.selectbox("Seleccionar Trimestre:", [1, 2])
else:
    selected_trimester = st.selectbox("Seleccionar Trimestre:", data['Trimestre'].unique(), index=len(data['Trimestre'].unique())-1)

# Filter data based on user selection
filtered_data = data[(data['Periodo'] == selected_year) & (data['Trimestre'] == selected_trimester)]

# Bar chart using Matplotlib and Seaborn
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=filtered_data,
    x='Entidad_Federativa',
    y='Poblacion_Economicamente_Activa',
    hue='Sexo',
    palette=['steelblue', 'magenta']
)
plt.title(f'Población Económica Activa en {selected_year} - Trimestre {selected_trimester}')
plt.xlabel('Entidad Federativa')
plt.ylabel('Población (millones de habitantes)')
plt.xticks(rotation=45, ha='right')
plt.legend(title='Sexo')

# Display the chart
st.pyplot(fig)
