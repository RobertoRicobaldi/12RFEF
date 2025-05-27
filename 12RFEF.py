import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
from io import BytesIO
from PIL import Image

# --------------------- AUTENTICACIÓN ---------------------
def login():
    st.title("🔐 Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if username == "admin" and password == "admin":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

def logout():
    st.session_state["logged_in"] = False
    st.rerun()

# Inicializar sesión
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()
else:
    st.sidebar.success("Sesión iniciada como admin ✅")
    if st.sidebar.button("Cerrar sesión"):
        logout()

# Título de la aplicación
st.title("Análisis de Jugadoras de 1-2 RFEF")

# Define las rutas del archivo Excel
local_path = r"C:\Users\rricobaldi\Desktop\OPTA - Provision\Informes Power BI\Ligas\1 RFEF\Futboleras\12 RFEF 23Enero2025.xlsx"
github_url = "https://github.com/RobertoRicobaldi/12RFEF/raw/main/12%20RFEF%2023Enero2025.xlsx"

# Función para obtener la ruta del archivo Excel
def get_file_path():
    # Verificar si el archivo existe en la ruta local
    if os.path.exists(local_path):
        return local_path
    else:
        # Si no existe en local, intentar cargar desde GitHub
        response = requests.get(github_url)
        if response.status_code == 200:
            return github_url
        else:
            st.error(f"Error: No se encontró el archivo Excel en ninguna ruta. Rutas verificadas: {local_path}, {github_url}")
            return None

# Función para cargar los datos desde el Excel
@st.cache_data
def load_data():
    try:
        file_path = get_file_path()
        if file_path is None:
            return pd.DataFrame()
        
        if file_path.startswith("http"):
            response = requests.get(file_path)
            if response.status_code == 200:
                excel_data = BytesIO(response.content)
                data = pd.read_excel(excel_data, engine='openpyxl')
            else:
                st.error(f"Error al descargar el archivo desde GitHub. Código de estado: {response.status_code}")
                return pd.DataFrame()
        else:
            data = pd.read_excel(file_path, engine='openpyxl')

        st.success("Datos cargados correctamente.")
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return pd.DataFrame()

# Cargar los datos
df = load_data()

# Mostrar resumen de carga
st.info(f"📊 Datos cargados correctamente: **{len(df)} registros** de jugadoras.")

# Mostrar una vista previa de los datos cargados
st.write("### Vista previa de los datos cargados:")
if not df.empty:
    st.write(df.head(10))  # Mostrar 10 filas en lugar de 5
else:
    st.write("No hay datos para mostrar.")

# Verificar si la columna 'EQUIPO' está presente
if not df.empty and 'EQUIPO' not in df.columns:
    st.error("La columna 'EQUIPO' no se encuentra en el archivo Excel.")
else:
    st.write("La columna 'EQUIPO' está presente en el archivo Excel.")

# Función para cargar los escudos desde el archivo Modelo de datos 12RFEF 2025.xlsx
def cargar_escudos():
    try:
        # Ruta local del archivo de escudos
        local_path_escudos = r"C:\Users\rricobaldi\Desktop\OPTA - Provision\Informes Power BI\Ligas\1 RFEF\Futboleras\Modelo de datos 12RFEF 2025.xlsx"
        
        # URL de descarga directa del archivo en GitHub
        github_url_escudos = "https://github.com/RobertoRicobaldi/12RFEF/raw/main/Modelo%20de%20datos%2012RFEF%202025.xlsx"
        
        # Verificar si el archivo existe en la ruta local
        if os.path.exists(local_path_escudos):
            df_escudos = pd.read_excel(local_path_escudos)
        else:
            # Si no existe en local, intentar cargar desde GitHub
            response = requests.get(github_url_escudos)
            if response.status_code == 200:
                excel_data = BytesIO(response.content)
                df_escudos = pd.read_excel(excel_data)
            else:
                st.error(f"Error al cargar el archivo de escudos desde GitHub. Código de estado: {response.status_code}")
                return {}
        
        # Crear un diccionario que asocie cada equipo con su URL de escudo
        escudos_dict = dict(zip(df_escudos["EQUIPO"], df_escudos["URL_ESCUDO"]))
        return escudos_dict
    except Exception as e:
        st.error(f"Error al cargar los escudos: {e}")
        return {}

# Cargar los escudos
escudos_dict = cargar_escudos()

# Función para cargar una imagen desde una URL con manejo de errores
def cargar_imagen_desde_url(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es 200
        return Image.open(BytesIO(response.content))
    except Exception as e:
        st.warning(f"No se pudo cargar la imagen desde {url}. Error: {e}")
        return None

# Función para mostrar una tabla con escudos dentro de la tabla
def mostrar_tabla_con_escudos(df, escudos_dict):
    # Crear una nueva columna con el código HTML para mostrar los escudos
    df["ESCUDO"] = df["EQUIPO"].apply(
        lambda equipo: f'<img src="{escudos_dict.get(equipo, "")}" width="50">'
    )
    
    # Reordenar las columnas para que el escudo aparezca junto al equipo y la edad después del nombre
    columnas = ["ESCUDO", "EQUIPO", "NOMBRE", "EDAD"] + [col for col in df.columns if col not in ["ESCUDO", "EQUIPO", "NOMBRE", "EDAD"]]
    df = df[columnas]
    
    # Convertir el DataFrame a HTML
    tabla_html = df.to_html(escape=False, index=False)
    
    # Mostrar la tabla con HTML personalizado
    st.write(tabla_html, unsafe_allow_html=True)

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
def pagina_filtros(escudos_dict):
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

    # Mostrar vista previa de los datos filtrados
    st.write("### Vista previa de los datos filtrados:")
    mostrar_tabla_con_escudos(df_filtrado.head(10), escudos_dict)  # Mostrar 10 filas con escudos

    # Mostrar todas las jugadoras del equipo, incluso las que no han jugado
    if equipo_seleccionado != "Todos":
        todas_las_jugadoras = df[df["EQUIPO"] == equipo_seleccionado]
        st.write(f"### Todas las jugadoras de {equipo_seleccionado}")
        mostrar_tabla_con_escudos(todas_las_jugadoras, escudos_dict)

    # Mostrar ranking por goles
    st.write("### Ranking de Jugadoras por Goles")
    ranking_goles = df_filtrado.sort_values(by="Goles", ascending=False)
    mostrar_tabla_con_escudos(ranking_goles.head(10), escudos_dict)  # Mostrar top 10 con escudos

    # Exportar datos
    st.write("### Exportar Datos")
    exportar_datos(ranking_goles, "ranking_goles")

# Página de Búsqueda de Jugadoras
def pagina_busqueda(escudos_dict):
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

    # Filtrar por posición (POS)
    if "POS" in df.columns:
        posiciones = df["POS"].unique()
        posicion_seleccionada = st.sidebar.selectbox("Selecciona una posición", ["Todas"] + list(posiciones), key="busqueda_pos")
    else:
        st.error("La columna 'POS' no se encuentra en el archivo Excel.")
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

    if posicion_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["POS"] == posicion_seleccionada]

    df_filtrado = df_filtrado[
        (df_filtrado["PJ"] >= rango_pj[0]) & (df_filtrado["PJ"] <= rango_pj[1]) &
        (df_filtrado["EDAD"] >= rango_edad[0]) & (df_filtrado["EDAD"] <= rango_edad[1]) &
        (df_filtrado["MJ"] >= rango_mj[0]) & (df_filtrado["MJ"] <= rango_mj[1])
    ]

    # Mostrar el listado de jugadoras filtradas
    st.write("### Listado de Jugadoras Filtradas")
    mostrar_tabla_con_escudos(df_filtrado.head(10), escudos_dict)  # Mostrar 10 filas con escudos

    # Búsqueda de jugadoras
    jugadoras = df_filtrado["NOMBRE"].unique()
    jugadora_seleccionada = st.selectbox("Selecciona una jugadora", jugadoras)

    if jugadora_seleccionada:
        # Obtener todos los registros de la jugadora seleccionada
        jugadora_data = df[df["NOMBRE"] == jugadora_seleccionada]

        # Resumen de estadísticas
        st.write(f"#### Resumen de {jugadora_seleccionada}")
        mostrar_tabla_con_escudos(jugadora_data, escudos_dict)

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
def pagina_comparativa(escudos_dict):
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

        # Mostrar estadísticas de ambas jugadoras
        st.write(f"#### Estadísticas de {jugadora_1} y {jugadora_2}")
        st.write(f"**{jugadora_1}:**")
        mostrar_tabla_con_escudos(jugadora_1_data, escudos_dict)
        st.write(f"**{jugadora_2}:**")
        mostrar_tabla_con_escudos(jugadora_2_data, escudos_dict)

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

        # Exportar datos de la comparativa
        st.write("### Exportar Datos")
        datos_comparativa = pd.concat([jugadora_1_data, jugadora_2_data])
        exportar_datos(datos_comparativa, f"comparativa_{jugadora_1}_vs_{jugadora_2}")

# Validar que los datos estén correctamente cargados antes de continuar
if df.empty or escudos_dict == {}:
    st.error("❌ No se han podido cargar correctamente los datos o los escudos.")
    st.button("🔄 Recargar", on_click=st.rerun)
    st.stop()

# Navegación en la barra lateral
pagina = st.sidebar.radio(
    "Selecciona una página",
    ["Filtros y Datos", "Búsqueda de Jugadoras", "Comparativa de Jugadoras"]
)

# Mostrar la página seleccionada
if pagina == "Filtros y Datos":
    pagina_filtros(escudos_dict)
elif pagina == "Búsqueda de Jugadoras":
    pagina_busqueda(escudos_dict)
elif pagina == "Comparativa de Jugadoras":
    pagina_comparativa(escudos_dict)