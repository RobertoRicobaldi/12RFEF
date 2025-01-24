import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Título de la aplicación
st.title("Análisis de Jugadoras de 1-2 RFEF")

# Función para obtener la ruta del archivo Excel
def get_file_path():
    # Ruta local
    local_path = r"C:\Users\rricobaldi\Desktop\OPTA - Provision\Informes Power BI\Ligas\1 RFEF\Futboleras\12 RFEF 23Enero2025.xlsx"
    
    # Ruta para Streamlit Sharing
    streamlit_path = "main/12 RFEF 23Enero2025.xlsx"
    
    # Verificar si el archivo existe en la ruta local
    if os.path.exists(local_path):
        st.write("Usando ruta local:", local_path)
        return local_path
    # Verificar si el archivo existe en la ruta de Streamlit Sharing
    elif os.path.exists(streamlit_path):
        st.write("Usando ruta de Streamlit:", streamlit_path)
        return streamlit_path
    else:
        st.error(f"Error: No se encontró el archivo Excel en ninguna ruta. Rutas verificadas: {local_path}, {streamlit_path}")
        return None

# Cargar el archivo Excel
@st.cache_data
def load_data():
    try:
        # Obtener la ruta del archivo
        file_path = get_file_path()
        if file_path is None:
            return pd.DataFrame()
        
        # Cargar los datos
        data = pd.read_excel(file_path, engine='openpyxl')
        st.success("Datos cargados correctamente.")
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return pd.DataFrame()

# Cargar los datos
df = load_data()

# Verificar las columnas del DataFrame
if not df.empty:
    st.write("Columnas del DataFrame:", df.columns.tolist())

# Mostrar una vista previa de los datos
st.write("### Vista previa de los datos cargados:")
st.write(df.head())

# Función para exportar datos
def exportar_datos(data, nombre_archivo):
    formato = st.selectbox("Selecciona el formato de exportación", ["CSV", "Excel"], key=f"formato_{nombre_archivo}")
    if formato == "CSV":
        st.download_button(
            label="Descargar como CSV",
            data=data.to_csv(index=False).encode('utf-8'),
            file_name=f"{nombre_archivo}.csv",
            mime="text/csv"
        )
    elif formato == "Excel":
        st.download_button(
            label="Descargar como Excel",
            data=data.to_excel(index=False, engine='openpyxl'),
            file_name=f"{nombre_archivo}.xlsx",
            mime="application/vnd.ms-excel"
        )

# Página de Filtros y Datos Generales
def pagina_filtros():
    st.write("### Filtros y Datos Generales")
    st.write("Utiliza los filtros para explorar los datos de las jugadoras.")

    # Filtros en la barra lateral
    st.sidebar.header("Filtros")

    # Seleccionar todas las jugadoras o filtrar por equipo
    if "EQUIPO" in df.columns:
        equipos = df["EQUIPO"].unique()
        equipo_seleccionado = st.sidebar.selectbox("Selecciona un equipo", ["Todos"] + list(equipos))
    else:
        st.error("La columna 'EQUIPO' no se encuentra en el archivo Excel.")
        return

    # Filtrar por división (LIGA)
    if "LIGA" in df.columns:
        divisiones = df["LIGA"].unique()
        division_seleccionada = st.sidebar.selectbox("Selecciona una división", ["Todas"] + list(divisiones))
    else:
        st.error("La columna 'LIGA' no se encuentra en el archivo Excel.")
        return

    # Filtrar por edad (rango)
    if "EDAD" in df.columns:
        min_edad = int(df["EDAD"].min())
        max_edad = int(df["EDAD"].max())
        rango_edad = st.sidebar.slider("Selecciona un rango de edad", min_edad, max_edad, (min_edad, max_edad))
    else:
        st.error("La columna 'EDAD' no se encuentra en el archivo Excel.")
        return

    # Filtrar por partidos jugados (PJ)
    if "PJ" in df.columns:
        min_pj = int(df["PJ"].min())
        max_pj = int(df["PJ"].max())
        rango_pj = st.sidebar.slider("Selecciona un rango de partidos jugados", min_pj, max_pj, (min_pj, max_pj))
    else:
        st.error("La columna 'PJ' no se encuentra en el archivo Excel.")
        return

    # Aplicar filtros
    if equipo_seleccionado == "Todos":
        df_filtrado = df.copy()
    else:
        df_filtrado = df[df["EQUIPO"] == equipo_seleccionado]

    if division_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["LIGA"] == division_seleccionada]

    df_filtrado = df_filtrado[
        (df_filtrado["EDAD"] >= rango_edad[0]) & (df_filtrado["EDAD"] <= rango_edad[1]) &
        (df_filtrado["PJ"] >= rango_pj[0]) & (df_filtrado["PJ"] <= rango_pj[1])
    ]

    # Mostrar todas las jugadoras del equipo, incluso las que no han jugado
    if equipo_seleccionado != "Todos":
        todas_las_jugadoras = df[df["EQUIPO"] == equipo_seleccionado]
        st.write(f"### Todas las jugadoras de {equipo_seleccionado}")
        st.dataframe(todas_las_jugadoras)

    # Mostrar ranking por goles
    st.write("### Ranking de Jugadoras por Goles")
    ranking_goles = df_filtrado.sort_values(by="Goles", ascending=False)
    st.dataframe(ranking_goles[["NOMBRE", "EQUIPO", "LIGA", "Goles", "Asist.", "TA", "TR", "MJ", "PJ"]])

    # Exportar datos
    st.write("### Exportar Datos")
    exportar_datos(ranking_goles, "ranking_goles")

# Página de Búsqueda de Jugadoras
def pagina_busqueda():
    st.write("### Búsqueda de Jugadoras")
    st.write("Selecciona una jugadora para ver su resumen de estadísticas y gráficos.")

    # Filtros en la barra lateral
    st.sidebar.header("Filtros")

    # Seleccionar todas las jugadoras o filtrar por equipo
    if "EQUIPO" in df.columns:
        equipos = df["EQUIPO"].unique()
        equipo_seleccionado = st.sidebar.selectbox("Selecciona un equipo", ["Todos"] + list(equipos), key="busqueda_equipo")
    else:
        st.error("La columna 'EQUIPO' no se encuentra en el archivo Excel.")
        return

    # Filtrar por partidos jugados (PJ)
    if "PJ" in df.columns:
        min_pj = int(df["PJ"].min())
        max_pj = int(df["PJ"].max())
        rango_pj = st.sidebar.slider("Selecciona un rango de partidos jugados", min_pj, max_pj, (min_pj, max_pj), key="busqueda_pj")
    else:
        st.error("La columna 'PJ' no se encuentra en el archivo Excel.")
        return

    # Filtrar por edad (rango)
    if "EDAD" in df.columns:
        min_edad = int(df["EDAD"].min())
        max_edad = int(df["EDAD"].max())
        rango_edad = st.sidebar.slider("Selecciona un rango de edad", min_edad, max_edad, (min_edad, max_edad), key="busqueda_edad")
    else:
        st.error("La columna 'EDAD' no se encuentra en el archivo Excel.")
        return

    # Filtrar por minutos jugados (MJ)
    if "MJ" in df.columns:
        min_mj = int(df["MJ"].min())
        max_mj = int(df["MJ"].max())
        rango_mj = st.sidebar.slider("Selecciona un rango de minutos jugados", min_mj, max_mj, (min_mj, max_mj), key="busqueda_mj")
    else:
        st.error("La columna 'MJ' no se encuentra en el archivo Excel.")
        return

    # Aplicar filtros
    if equipo_seleccionado == "Todos":
        df_filtrado = df.copy()
    else:
        df_filtrado = df[df["EQUIPO"] == equipo_seleccionado]

    df_filtrado = df_filtrado[
        (df_filtrado["PJ"] >= rango_pj[0]) & (df_filtrado["PJ"] <= rango_pj[1]) &
        (df_filtrado["EDAD"] >= rango_edad[0]) & (df_filtrado["EDAD"] <= rango_edad[1]) &
        (df_filtrado["MJ"] >= rango_mj[0]) & (df_filtrado["MJ"] <= rango_mj[1])
    ]

    # Búsqueda de jugadoras
    jugadoras = df_filtrado["NOMBRE"].unique()
    jugadora_seleccionada = st.selectbox("Selecciona una jugadora", jugadoras)

    if jugadora_seleccionada:
        # Obtener todos los registros de la jugadora seleccionada
        jugadora_data = df[df["NOMBRE"] == jugadora_seleccionada]

        # Resumen de estadísticas
        st.write(f"#### Resumen de {jugadora_seleccionada}")
        st.write(f"**Equipos y Ligas:**")
        for _, row in jugadora_data.iterrows():
            st.write(f"- **Equipo:** {row['EQUIPO']}, **Liga:** {row['LIGA']}, **Goles:** {row['Goles']}, "
                     f"**Asistencias:** {row['Asist.']}, **Tarjetas Amarillas:** {row['TA']}, "
                     f"**Tarjetas Rojas:** {row['TR']}, **Minutos Jugados:** {row['MJ']}, "
                     f"**Partidos Jugados:** {row['PJ']}")

        # Radar chart para la jugadora seleccionada
        st.write("#### Radar Chart de Métricas")
        metricas = ["Goles", "Asist.", "TA", "TR", "PJ"]
        valores = jugadora_data[metricas].sum().tolist()

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=valores,
            theta=metricas,
            fill='toself',
            name=jugadora_seleccionada,
            line_color='darkblue'  # Azul oscuro
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=True
        )
        st.plotly_chart(fig)

        # Gráfico de barras para la jugadora seleccionada
        st.write("#### Gráfico de Barras")
        fig_bar = px.bar(
            x=metricas,
            y=valores,
            labels={"x": "Métrica", "y": "Valor"},
            title=f"Estadísticas de {jugadora_seleccionada}",
            color_discrete_sequence=['darkblue']  # Azul oscuro
        )
        st.plotly_chart(fig_bar)

        # Exportar datos de la jugadora seleccionada
        st.write("### Exportar Datos")
        exportar_datos(jugadora_data, f"datos_{jugadora_seleccionada}")

# Página de Comparativa de Jugadoras
def pagina_comparativa():
    st.write("### Comparativa de Jugadoras")
    st.write("Selecciona dos jugadoras para comparar sus estadísticas.")

    # Filtros en la barra lateral
    st.sidebar.header("Filtros")

    # Seleccionar todas las jugadoras o filtrar por equipo
    if "EQUIPO" in df.columns:
        equipos = df["EQUIPO"].unique()
        equipo_seleccionado = st.sidebar.selectbox("Selecciona un equipo", ["Todos"] + list(equipos), key="comparativa_equipo")
    else:
        st.error("La columna 'EQUIPO' no se encuentra en el archivo Excel.")
        return

    # Filtrar por partidos jugados (PJ)
    if "PJ" in df.columns:
        min_pj = int(df["PJ"].min())
        max_pj = int(df["PJ"].max())
        rango_pj = st.sidebar.slider("Selecciona un rango de partidos jugados", min_pj, max_pj, (min_pj, max_pj), key="comparativa_pj")
    else:
        st.error("La columna 'PJ' no se encuentra en el archivo Excel.")
        return

    # Aplicar filtros
    if equipo_seleccionado == "Todos":
        df_filtrado = df.copy()
    else:
        df_filtrado = df[df["EQUIPO"] == equipo_seleccionado]

    df_filtrado = df_filtrado[
        (df_filtrado["PJ"] >= rango_pj[0]) & (df_filtrado["PJ"] <= rango_pj[1])
    ]

    # Selección de jugadoras para comparar
    jugadoras = df_filtrado["NOMBRE"].unique()
    jugadora_1 = st.selectbox("Selecciona la primera jugadora", jugadoras, key="jugadora_1")
    jugadora_2 = st.selectbox("Selecciona la segunda jugadora", jugadoras, key="jugadora_2")

    if jugadora_1 and jugadora_2:
        jugadora_1_data = df[df["NOMBRE"] == jugadora_1]
        jugadora_2_data = df[df["NOMBRE"] == jugadora_2]

        # Radar chart comparativo
        st.write("#### Radar Chart Comparativo")
        metricas = ["Goles", "Asist.", "TA", "TR", "PJ"]
        valores_1 = jugadora_1_data[metricas].sum().tolist()
        valores_2 = jugadora_2_data[metricas].sum().tolist()

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores_1,
            theta=metricas,
            fill='toself',
            name=jugadora_1,
            line_color='darkblue'  # Azul oscuro
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=valores_2,
            theta=metricas,
            fill='toself',
            name=jugadora_2,
            line_color='orange'  # Naranja
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=True,
            title="Comparativa de Métricas (Radar Chart)"
        )
        st.plotly_chart(fig_radar)

        # Gráfico de barras comparativo
        st.write("#### Gráfico de Barras Comparativo")
        fig_barras = go.Figure()
        fig_barras.add_trace(go.Bar(
            x=metricas,
            y=valores_1,
            name=jugadora_1,
            marker_color='darkblue'  # Azul oscuro
        ))
        fig_barras.add_trace(go.Bar(
            x=metricas,
            y=valores_2,
            name=jugadora_2,
            marker_color='orange'  # Naranja
        ))
        fig_barras.update_layout(
            barmode='group',
            title="Comparativa de Métricas (Gráfico de Barras)",
            xaxis_title="Métricas",
            yaxis_title="Valor",
            showlegend=True
        )
        st.plotly_chart(fig_barras)

        # Mostrar estadísticas de ambas jugadoras
        st.write(f"#### Estadísticas de {jugadora_1} y {jugadora_2}")
        st.write(f"**{jugadora_1}:**")
        st.write(jugadora_1_data[["EQUIPO", "LIGA", "Goles", "Asist.", "TA", "TR", "PJ"]])
        st.write(f"**{jugadora_2}:**")
        st.write(jugadora_2_data[["EQUIPO", "LIGA", "Goles", "Asist.", "TA", "TR", "PJ"]])

        # Exportar datos de la comparativa
        st.write("### Exportar Datos")
        datos_comparativa = pd.concat([jugadora_1_data, jugadora_2_data])
        exportar_datos(datos_comparativa, f"comparativa_{jugadora_1}_vs_{jugadora_2}")

# Navegación en la barra lateral
pagina = st.sidebar.radio(
    "Selecciona una página",
    ["Filtros y Datos", "Búsqueda de Jugadoras", "Comparativa de Jugadoras"]
)

# Mostrar la página seleccionada
if pagina == "Filtros y Datos":
    pagina_filtros()
elif pagina == "Búsqueda de Jugadoras":
    pagina_busqueda()
elif pagina == "Comparativa de Jugadoras":
    pagina_comparativa()