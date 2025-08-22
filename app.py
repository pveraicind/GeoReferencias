import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

st.set_page_config(page_title="GeoReferencias FRNSW", layout="wide")
st.title("GeoReferencias FRNSW")

# Cargar datos
df = pd.read_excel('georeferencias.xlsx')
st.subheader("Datos de Salas")
st.dataframe(df)


# Filtro por tipo de sala usando la columna 'tipo'
tipos_disponibles = df['Tipo'].dropna().unique().tolist()
opciones_tipo = ['Todas'] + tipos_disponibles
tipo_sala = st.radio('Filtrar por tipo de sala:', opciones_tipo, index=0)

if tipo_sala == 'Todas':
    df_tipo = df
else:
    df_tipo = df[df['Tipo'] == tipo_sala]

# Filtro para seleccionar salas por nombre dentro del grupo
salas = df_tipo['Nombre Sala'].unique().tolist()
seleccionar_todas = st.checkbox('Seleccionar todas las salas del grupo mostrado', value=True)
if seleccionar_todas:
    salas_seleccionadas = salas
else:
    salas_seleccionadas = st.multiselect('Selecciona una o más salas para mostrar en el mapa:', salas, default=salas)

# Filtrar el DataFrame según la selección
df_filtrado = df_tipo[df_tipo['Nombre Sala'].isin(salas_seleccionadas)]

# Crear mapa base
m = folium.Map(location=[-40.5740, -73.1322], tiles='OpenStreetMap', zoom_start=11)

# Agregar marcadores solo para las salas seleccionadas
for i, row in df_filtrado.iterrows():
    lat = row['Latitud']
    lng = row['Longitud']
    popup = f"Nombre Sala: {row['Nombre Sala']}<br>Lat: {lat}<br>Lng: {lng}<br><a href='https://www.google.com/maps?q={lat},{lng}&hl=es-PY&gl=py&shorturl=1' target='_blank'>Google Maps</a>"
    folium.Marker(location=[lat, lng], popup=popup, icon=folium.Icon(color='blue')).add_to(m)

# Agregar HeatMap solo para las salas seleccionadas
if not df_filtrado.empty:
    heat_data = df_filtrado[['Latitud', 'Longitud', 'Producción anual']].values.tolist()
    HeatMap(heat_data, gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1: 'red'}).add_to(m)

# Mostrar mapa en Streamlit
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Mapa de Salas y Heatmap")
    st_folium(m, width=900, height=600)

# Gráfico de barras de Producción anual para las salas seleccionadas
import matplotlib.pyplot as plt
with col2:
    st.subheader("Producción anual por sala")
    if not df_filtrado.empty:
        fig, ax = plt.subplots(figsize=(5, 6))
        df_filtrado_sorted = df_filtrado.sort_values('Producción anual', ascending=False)
        ax.barh(df_filtrado_sorted['Nombre Sala'], df_filtrado_sorted['Producción anual'], color='orange')
        ax.set_xlabel('Litros')
        ax.set_ylabel('Sala')
        ax.invert_yaxis()
        st.pyplot(fig)
    else:
        st.info('No hay datos para mostrar el gráfico.')
