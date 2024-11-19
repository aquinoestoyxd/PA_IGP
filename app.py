import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Cargar el archivo XLSX
archivo_xlsx = 'Catalogo1960_2023.xlsx'  # Cambia esto con la ruta del archivo
df = pd.read_excel(archivo_xlsx)

# Configuración del título y la descripción del dashboard
st.title("Catálogo Sísmico del Perú")
st.write("Este dashboard permite explorar el catálogo sísmico elaborado por el IGP con datos desde 1960.")

#1 Mostrar los primeros registros de la base de datos
st.subheader("Vista general de los datos")
st.write(df)


#2 Histograma de la magnitud de los sismos
st.subheader("Distribución de la Magnitud de los Sismos")
fig_histograma = px.histogram(df, x='MAGNITUD', nbins=50, title="Histograma de Magnitud de Sismos")
st.plotly_chart(fig_histograma)



# 3Gráfico de dispersión para magnitud vs. profundidad
st.subheader("Magnitud vs. Profundidad de los Sismos")
fig_dispersion = px.scatter(df, x='PROFUNDIDAD', y='MAGNITUD',
                            labels={'PROFUNDIDAD': 'Profundidad (km)', 'MAGNITUD': 'Magnitud'},
                            title="Relación entre Magnitud y Profundidad")
st.plotly_chart(fig_dispersion)


#4
# Cálculo del resumen estadístico
# Cálculo del resumen estadístico
promedio_magnitud = df['MAGNITUD'].mean()
std_magnitud = df['MAGNITUD'].std()
max_magnitud = df['MAGNITUD'].max()
min_magnitud = df['MAGNITUD'].min()

promedio_profundidad = df['PROFUNDIDAD'].mean()
std_profundidad = df['PROFUNDIDAD'].std()
total_sismos = df.shape[0]

# Mostrar el resumen estadístico
st.subheader("Resumen Estadístico de los Sismos")
st.write(f"**Total de sismos registrados**: {total_sismos}")
st.write(f"**Promedio de Magnitud**: {promedio_magnitud:.2f}")
st.write(f"**Desviación Estándar de la Magnitud**: {std_magnitud:.2f}")
st.write(f"**Máxima Magnitud Registrada**: {max_magnitud:.2f}")
st.write(f"**Mínima Magnitud Registrada**: {min_magnitud:.2f}")
st.write(f"**Promedio de Profundidad**: {promedio_profundidad:.2f} km")
st.write(f"**Desviación Estándar de la Profundidad**: {std_profundidad:.2f} km")




m = folium.Map(location=[-9.19, -75.0152], zoom_start=5)
# Añadir marcadores para cada sismo en el catálogo
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row['LATITUD'], row['LONGITUD']],
        radius=3,
        popup=f"Magnitud: {row['MAGNITUD']}",
        color="red",
        fill=True,
        fill_color="red"
    ).add_to(m)
# Mostrar el mapa en Streamlit
st.subheader("Mapa de Sismos en Perú")
st.write("")
st_folium(m, width=700, height=500)