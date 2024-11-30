import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from st_aggrid import AgGrid
from streamlit_option_menu import option_menu
from st_aggrid.grid_options_builder import GridOptionsBuilder

#descargar el archivo
file_path = "Catalogo1960_2023.xlsx"
data = pd.read_excel(file_path)

shapefile_path = "DEPARTAMENTOS.shp"
departments = gpd.read_file(shapefile_path)

if not departments.crs:
    departments = departments.set_crs("EPSG:4326")
else:
    # Transformar al CRS requerido por Folium
    departments = departments.to_crs("EPSG:4326")

#Para trabajar los años
data['FECHA_UTC'] = pd.to_datetime(data['FECHA_UTC'], format='%Y%m%d', errors='coerce')
data['AÑO'] = data['FECHA_UTC'].dt.year

geometry = gpd.points_from_xy(data['LONGITUD'], data['LATITUD'])
geo_df = gpd.GeoDataFrame(data, geometry=geometry)
geo_df = geo_df.set_crs("EPSG:4326")


geo_df = geo_df.set_crs(departments.crs)
result = gpd.sjoin(geo_df, departments, how="left", predicate="within")
data['DEPARTAMENTO'] = result['DEPARTAMEN'].str.strip().str.upper()  # Asignar nombre del departamento

# Clasificar con base en coordenadas (Latitud y Longitud)
lat_min, lat_max = -18.35, -0.05
lon_min, lon_max = -81.33, -68.65

# Clasificar puntos "EN EL MAR"
en_el_mar = (
    (data['LATITUD'] >= lat_min) & (data['LATITUD'] <= lat_max) &
    (data['LONGITUD'] >= lon_min) & (data['LONGITUD'] <= lon_max) &
    (data['DEPARTAMENTO'].isna()) ) # Solo si no pertenece a un departamento
data.loc[en_el_mar, 'DEPARTAMENTO'] = "EN EL MAR"

# Clasificar puntos "EN OTRO PAÍS"
en_otro_pais = (
    (data['LATITUD'] < lat_min) | (data['LATITUD'] > lat_max) |
    (data['LONGITUD'] < lon_min) | (data['LONGITUD'] > lon_max))

data.loc[en_otro_pais, 'DEPARTAMENTO'] = "EN OTRO PAÍS"
data['DEPARTAMENTO'] = data['DEPARTAMENTO'].fillna("SIN UBICACIÓN DEFINIDA")
#Sidebar
with st.sidebar:
    selected = option_menu(
        "Menú Principal",  # Título del menú
        ["Inicio", "Vista General", "Gráficas", "Mapa Interactivo","Prevencion","Sismos más Fuertes"],  # Opciones principales
        icons=["house", "table", "bar-chart", "geo-alt","shield-exclamation","bolt"],  # Íconos
        menu_icon="cast",  # Ícono del menú
        default_index=0,  # Selección inicial
        styles={
            "container": {"padding": "5px", "background-color": "#1a1a1a"},  # Fondo oscuro
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px",
                "color": "#cfcfcf",  # Color de texto claro
                "border-radius": "5px",
            },
            "nav-link-selected": {
                "background-color": "#007bff",  # Azul
                "color": "white",
            },
        },
    )

    # Submenú de Graficas
    if selected == "Gráficas":
        sub_selected = option_menu(
            "Gráficas",  # Título del submenú
            ["Gráfica Interactiva", "Gráfico de Datos"],  # Opciones del submenú
            icons=["bar-chart", "graph-up"],  # Íconos
            menu_icon="bar-chart",  # Ícono del submenú
            default_index=0,  # Selección inicial
            styles={
                "container": {"padding": "5px"},
                "nav-link": {
                    "font-size": "14px",
                    "color": "#cfcfcf",
                    "margin": "2px",
                },
                "nav-link-selected": {
                    "background-color": "#0056b3",
                    "color": "white",
                },
            },
        )
    else:
        sub_selected = None

    if selected == "Mapa Interactivo":
        map_selected = option_menu(
            "Mapas Interactivos",
            ["Mapa por Rangos de Magnitud", "Mapa por Departamento"],
            icons=["map", "pin-map"],
            menu_icon="geo-alt",
            default_index=0,
            styles={
                "container": {"padding": "5px"},
                "nav-link": {
                    "font-size": "14px",
                    "color": "#cfcfcf",
                    "margin": "2px",
                },
                "nav-link-selected": {
                    "background-color": "#0056b3",
                    "color": "white",
                },
            },
        )
    else:
        map_selected = None
#La seleccion para los submenus
if selected == "Inicio":

    st.title("Análisis de Sismos en el Perú (1960-2023) 🌐")

    # Breve descripción del proyecto
    st.markdown("""
    ### Bienvenidos 👋
    Este proyecto presenta un análisis interactivo de los sismos ocurridos en el Perú entre 1960 y 2023, utilizando herramientas de visualización avanzadas como gráficos dinámicos y mapas interactivos. 
    El objetivo principal es facilitar la exploración de datos sísmicos para comprender patrones, tendencias y regiones más afectadas.

    #### ¿Qué encontrarás en este dashboard?
    - **Vista General:** Un resumen con los datos principales organizados en una tabla.
    - **Gráficas:** Visualizaciones interactivas para analizar sismos por departamento, rango de magnitud y más.
    - **Mapa Interactivo:** Localización geográfica de los sismos en el territorio peruano.

    ---
    """)

    # Sección de integrantes
    st.subheader("Integrantes del Equipo")
    st.markdown("""
    - **Andres Rodas**
    - **Jhan Mocaico**
    - **Juan Aquino**
    - **Dario Huerta**
    - **Anthony Zuñiga**
    """)

elif selected == "Vista General":
    st.title("Vista General 👀")
    st.write("Tabla extraída del archivo Excel:")
    gd = GridOptionsBuilder.from_dataframe(data)
    gd.configure_pagination(paginationAutoPageSize=True)
    gd.configure_side_bar()
    grid_options = gd.build()
    AgGrid(data, gridOptions=grid_options, theme='balham')

    # Botón de descarga
    @st.cache_data
    def convertir_a_csv(datos):
        return datos.to_csv(index=False).encode('utf-8')
    csv = convertir_a_csv(data)
    st.download_button(
        label="Descargar catálogo completo",
        data=csv,
        file_name='Catalogo_Sismico_Peru.csv',
        mime='text/csv',
    )

elif selected == "Gráficas":
    if sub_selected == "Gráfica Interactiva":
        st.title("Gráfica Interactiva")

        años_disponibles = sorted(data['AÑO'].dropna().unique(), reverse=True)  # Orden descendente
        año_seleccionado = st.selectbox("Selecciona el año:", años_disponibles)

        departamentos_disponibles = sorted(data['DEPARTAMENTO'].dropna().unique())
        depto_seleccionado = st.selectbox("Selecciona el departamento:",
                                          departamentos_disponibles)  # Selectbox para departamento

        # Filtrar los datos por el año y el departamento seleccionados
        datos_filtrados = data[(data['AÑO'] == año_seleccionado) &
                               (data['DEPARTAMENTO'] == depto_seleccionado)]
        datos_filtrados['PROFUNDIDAD_INVERSA'] = datos_filtrados['PROFUNDIDAD'].max() - datos_filtrados['PROFUNDIDAD']

        if not datos_filtrados.empty:
            total_sismos = len(datos_filtrados)
            sismo_mas_fuerte = datos_filtrados.loc[datos_filtrados['MAGNITUD'].idxmax()]
            st.write(
                f"### Resumen de Sismos en {depto_seleccionado} durante {año_seleccionado}:")
            st.metric(label="Número Total de Sismos", value=total_sismos)
            st.metric(
                label="Sismo Más Fuerte",
                value=f"{sismo_mas_fuerte['MAGNITUD']} Mw",
                help=(
                    f"Fecha: {sismo_mas_fuerte['FECHA_UTC']}\n"
                    f"Profundidad: {sismo_mas_fuerte['PROFUNDIDAD']} km"
                )
            )
            # Explicación sobre Mw
            st.caption("**Mw**: Magnitud Momento, una medida de la energía liberada por el sismo.")

            # Gráfico Rango de Magnitud
            bins = [0, 3, 4, 5, 6, 7, 10] #rangos
            labels = ["<3", "3-4", "4-5", "5-6", "6-7", ">7"]
            datos_filtrados['RANGO_MAGNITUD'] = pd.cut(datos_filtrados['MAGNITUD'], bins=bins, labels=labels)

            magnitud_counts = datos_filtrados['RANGO_MAGNITUD'].value_counts().sort_index()
            fig_magnitud = px.bar(
                x=magnitud_counts.index,
                y=magnitud_counts.values,
                title=f"MAGNITUD DE LOS SISMOS ",
                labels={"x": "Rango de Magnitud", "y": "Número de Sismos"},
                color=magnitud_counts.index,
            )
            st.plotly_chart(fig_magnitud)
            st.write(
                f"""
                        El gráfico de barras apiladas muestra la cantidad de sismos registrados en el departamento 
                        **{depto_seleccionado}** durante el año **{año_seleccionado}**, clasificados según rangos de magnitud. 
                        Esto permite identificar si predominan sismos de menor magnitud o si hay un número significativo 
                        de eventos más intensos.
                        """
            )
            fig_barras_invertidas = px.bar(
                datos_filtrados,
                x='FECHA_UTC',
                y='PROFUNDIDAD_INVERSA',
                title="PROFUNDIDAD DE SISMOS",
                labels={"FECHA_UTC": "Fecha", "PROFUNDIDAD_INVERSA": "Profundidad (invertida)"},
                text_auto=True
            )
            fig_barras_invertidas.update_yaxes(title="Profundidad (km)", autorange="reversed")
            st.plotly_chart(fig_barras_invertidas)
            st.write(
                """
                Este gráfico muestra la profundidad de los sismos registrados, donde barras más bajas representan profundidades mayores. Esta visualización facilita la comparación de profundidades de manera intuitiva, destacando los eventos más superficiales o profundos en función de su longitud visual.
                """
            )
        else:
            st.write("No hay datos para la selección realizada.")

    elif sub_selected == "Gráfico de Datos":
        st.title("Gráfico de Datos")
        st.subheader("Tendencia Anual de Sismos📈")

        sismos_por_año = data.groupby('AÑO').size()
        fig_tendencia = px.line(
            x=sismos_por_año.index,
            y=sismos_por_año.values,
            title="A) Número de Sismos por Año",
            labels={"x": "Año", "y": "Número de Sismos"},
        )
        st.plotly_chart(fig_tendencia) #grafo
        st.write(
            """
            - Este gráfico muestra cómo ha variado la cantidad de sismos registrados en cada año.
            - Es útil para identificar tendencias temporales, como períodos de mayor o menor actividad sísmica,
            y permite analizar la evolución de los eventos sísmicos a lo largo del tiempo.
            """
        )
        # GRAFICA DE BARRAS APILADAS
        bins = [0, 3, 4, 5, 6, 7, 10] #rangos
        labels = ["<3", "3-4", "4-5", "5-6", "6-7", ">7"]
        data['RANGO_MAGNITUD'] = pd.cut(data['MAGNITUD'], bins=bins, labels=labels)

        sismos_departamento = data.groupby(['DEPARTAMENTO', 'RANGO_MAGNITUD']).size().reset_index(name='CUENTA')

        fig_barras_apiladas = px.bar(
            sismos_departamento,
            x='DEPARTAMENTO',
            y='CUENTA',
            color='RANGO_MAGNITUD',
            title="B) Sismos Acumulados por Departamento y Rango de Magnitud",
            labels={"DEPARTAMENTO": "Departamento", "CUENTA": "Número de Sismos",
                    "RANGO_MAGNITUD": "Rango de Magnitud"},
            text_auto=True,  # Mostrar los valores directamente en las barras
        )
        fig_barras_apiladas.update_layout(
            xaxis=dict(title="Departamento", tickangle=45),  # Inclinación de etiquetas para mejor legibilidad
            yaxis=dict(
                title="Número de Sismos",
                tickformat=",",  # Formato para miles
            ),
            legend_title="Rango de Magnitud",
            barmode="stack",  # Barras apiladas
            margin=dict(t=50, b=150)  # Margen para evitar cortes en las etiquetas
        )
        st.plotly_chart(fig_barras_apiladas)
        st.write(
            """
            - Este gráfico representa el número total de sismos en cada departamento, desglosado por rangos de magnitud.
            - Los departamentos con mayor actividad sísmica son fácilmente identificables, y el desglose por magnitud permite
            entender la proporción de sismos de diferentes intensidades en cada región.
            """
        )

if selected == "Mapa Interactivo":
    if map_selected == "Mapa por Rangos de Magnitud":
        st.title("Mapa Interactivo: Rangos de Magnitud🗺")

        col1, col2 = st.columns([1, 2])  # Dividir en dos columnas
        with col1:
            st.header(""
                      ""
                      ""
                      "")
            magnitud_min, magnitud_max = st.slider(
                "Selecciona el rango de magnitud:",
                min_value=float(data['MAGNITUD'].min()),
                max_value=float(data['MAGNITUD'].max()),
                value=(6.0, 7.0),  # Valores iniciales
                step=0.1,
            )
            datos_filtrados = data[(data['MAGNITUD'] >= magnitud_min) & (data['MAGNITUD'] <= magnitud_max)]

        with col2:
            st.header("Mapa de Sismos")
            # Crear mapa
            mapa_rangos = folium.Map(location=[-9.19, -75.0152], zoom_start=6)  # Centrado en Perú
            for _, row in datos_filtrados.iterrows():
                folium.CircleMarker(
                    location=[row['LATITUD'], row['LONGITUD']],
                    radius=5,
                    color='red',
                    fill=True,
                    fill_color='red',
                    popup=f"Magnitud: {row['MAGNITUD']}<br>Fecha: {row['FECHA_UTC']}",
                ).add_to(mapa_rangos)
            st_folium(mapa_rangos, width=700, height=500)

    elif map_selected == "Mapa por Departamento":
        st.title("Mapa por Departamento 🧭")
        # Dividir en dos columnas
        col1, col2 = st.columns([2, 1])  # Ajusta las proporciones de las columnas (2:1)
        with col1:

            # Crear mapa base
            mapa_departamento = folium.Map(location=[-9.19, -75.0152], zoom_start=6)

            # Función para procesar la selección de departamentos
            def estilo_departamento(feature):
                return {"fillColor": "blue", "color": "black", "weight": 1, "fillOpacity": 0.5}
            folium.GeoJson(
                departments,
                name="Departamentos",
                tooltip=folium.GeoJsonTooltip(fields=["DEPARTAMEN"], aliases=["Departamento"]),
                style_function=estilo_departamento,
            ).add_to(mapa_departamento)

            # Mostrar el mapa en Streamlit
            output = st_folium(mapa_departamento, width=700, height=500)
        with col2:
            st.subheader("Características del Departamento")
            if output and output.get("last_active_drawing"):
                departamento_seleccionado = output["last_active_drawing"]["properties"]["DEPARTAMEN"]
                st.write(f"**Departamento Seleccionado:** {departamento_seleccionado}")
                datos_departamento = data[data["DEPARTAMENTO"] == departamento_seleccionado]

                if not datos_departamento.empty:
                    # Calcular características
                    total_sismos = int(len(datos_departamento))
                    promedio_magnitud = round(datos_departamento["MAGNITUD"].mean(), 2)
                    sismo_mas_fuerte = datos_departamento.loc[datos_departamento["MAGNITUD"].idxmax()]
                    magnitud_fuerte = round(sismo_mas_fuerte["MAGNITUD"], 1)
                    año_fuerte = int(sismo_mas_fuerte["AÑO"])

                    tabla = pd.DataFrame({
                        "Características": [
                            "Total de Sismos",
                            "Promedio de Magnitud",
                            "Sismo Más Fuerte",
                            "Año del Sismo Más Fuerte",
                        ],
                        "Valores": [
                            int(total_sismos),
                            promedio_magnitud,
                            magnitud_fuerte,
                            int(año_fuerte),
                        ],
                    })
                    tabla["Valores"] = tabla["Valores"].apply(
                        lambda x: f"{x:.2f}" if isinstance(x, float) else f"{x}"
                        # Solo redondear los flotantes a 2 decimales
                    )
                    st.table(tabla)
                else:
                    st.write("No hay datos disponibles para este departamento.")
            else:
                st.write("Selecciona un departamento en el mapa para ver sus características.")

if selected == "Prevencion":
    st.title("Prevención y Reacción ante Sismos🚧")

    st.markdown("""
    ### ¿Qué hacer antes de un sismo?
    - Asegura estanterías y objetos que puedan caer.
    - Identifica zonas seguras en tu hogar.
    - Ten un kit de emergencia listo.

    ### ¿Qué hacer durante un sismo?
    - Mantén la calma.
    - Aléjate de ventanas y objetos que puedan caer.
    - Ubícate en zonas de seguridad como debajo de una mesa resistente.

    ### ¿Qué hacer después de un sismo?
    - Revisa tu entorno en busca de posibles peligros.
    - Escucha las indicaciones de las autoridades.
    - No uses elevadores y evita entrar en edificios dañados.
    """)

    st.image("prevencion.png", caption="Prevención es clave", use_container_width=True)



elif selected == "Sismos más Fuertes":
    st.title("Sismos Más Fuertes Registrados 🌎")

    # Obtener los 4 sismos más fuertes
    sismos_fuertes = data.nlargest(4, 'MAGNITUD')

    st.write("### Los 4 sismos más fuertes registrados en el catálogo")
    st.table(sismos_fuertes[['FECHA_UTC', 'MAGNITUD', 'DEPARTAMENTO', 'LATITUD', 'LONGITUD']])

    # Mostrar imagen
    st.image("sismo.jpg", caption="Ejemplo de daños por sismos fuertes",
             use_container_width=True)
