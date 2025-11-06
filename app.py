# ==============================
# IMPORTACIONES
# ==============================
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path
import json

# ==============================
# CONFIGURACIÓN INICIAL
# ==============================
st.set_page_config(page_title="MORTALIDAD COLOMBIA 2019", layout="wide")
from PIL import Image

# Cargar imagen del logo
logo = Image.open("assets/LOGOSALLE.png")

# Mostrar en el encabezado
st.image(logo, width=250)  # Puedes ajustar el tamaño
st.title("📊 Análisis de Mortalidad en Colombia - 2019")
st.markdown(
    """
    **Elaborado por:** ALAIN ALEXANDER CAMACHO<br>
    **Maestría en Inteligencia Artificial** - Universidad de la Salle<br>
    Explora patrones de mortalidad en Colombia durante el año 2019 mediante visualizaciones interactivas de algunas estadísticas.
    """,
    unsafe_allow_html=True
)

# ==============================
# CARGA DE DATOS
# ==============================
DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_data():
    df_mortalidad = pd.read_excel(DATA_DIR / "Anexo1.NoFetal2019_CE_15-03-23.xlsx")
    df_codigos = pd.read_excel(DATA_DIR / "Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx")
    df_divipola = pd.read_excel(DATA_DIR / "DIVIPOLA_CE_.xlsx")
    return df_mortalidad, df_codigos, df_divipola

df, df_codigos, df_divipola = load_data()

# ==============================
# NORMALIZACIÓN DE DATOS
# ==============================
df.columns = df.columns.str.strip()
df_divipola.columns = df_divipola.columns.str.strip()

df["COD_DANE"] = df["COD_DANE"].astype(str).str.zfill(2)
df_divipola["COD_DANE"] = df_divipola["COD_DANE"].astype(str).str.zfill(2)

df_full = df.merge(df_divipola, on="COD_DANE", how="left")

# ==============================
# 1️⃣ MAPA: Muertes por departamento
# ==============================
st.subheader("🗺️ Distribución total de muertes por departamento")
map_data = df_full.groupby("DEPARTAMENTO").size().reset_index(name="Muertes")

with open(DATA_DIR / "colombia_departamentos.json", encoding="utf-8") as f:
    geojson = json.load(f)

fig_mapa = px.choropleth_mapbox(
    map_data,
    geojson=geojson,
    locations="DEPARTAMENTO",
    featureidkey="properties.NOMBRE_DPT",
    color="Muertes",
    color_continuous_scale="Reds",
    mapbox_style="carto-positron",
    zoom=4,
    center={"lat": 4.5709, "lon": -74.2973},
    opacity=0.7,
    labels={"Muertes": "Total de muertes"}
)
st.plotly_chart(fig_mapa, use_container_width=True)

# ==============================
# 2️⃣ LÍNEAS: Muertes por mes
# ==============================
st.subheader("📈 Total de muertes por mes en Colombia")

# Agrupar por la columna MES directamente
muertes_mes = df.groupby("MES").size().reset_index(name="Total")

# Crear gráfico de líneas
fig_lineas = px.line(
    muertes_mes,
    x="MES",
    y="Total",
    markers=True,
    title="Muertes por mes en Colombia",
    labels={"MES": "Mes", "Total": "Número de muertes"}
)

# Mostrar gráfico
st.plotly_chart(fig_lineas, use_container_width=True)


st.subheader("📊 5 ciudades más violentas (homicidios)")

# Filtrar homicidios por agresión
homicidios = df_full[df_full["MANERA_MUERTE"].str.contains("agresión", case=False, na=False)]

# Agrupar por municipio
ciudades_violentas = homicidios.groupby("MUNICIPIO").size().reset_index(name="Homicidios")

# Top 5
top5 = ciudades_violentas.sort_values("Homicidios", ascending=False).head(5)

# Gráfico
fig_bar_violencia = px.bar(
    top5,
    x="MUNICIPIO",
    y="Homicidios",
    color="MUNICIPIO",
    title="5 ciudades con más homicidios",
    labels={"MUNICIPIO": "Ciudad", "Homicidios": "Número de homicidios"}
)
# Mostrar gráfico
st.plotly_chart(fig_bar_violencia, use_container_width=True)


# ==============================
# 4️⃣ GRÁFICO CIRCULAR: 10 ciudades con menor mortalidad
# ==============================
st.subheader("🟢 10 ciudades con menor mortalidad")
muertes_ciudad = df_full.groupby("MUNICIPIO").size().reset_index(name="Total")
bottom10 = muertes_ciudad.sort_values("Total", ascending=True).head(10)
fig_pie = px.pie(bottom10, names="MUNICIPIO", values="Total",
                 title="10 ciudades con menor mortalidad", hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)


# ==============================
# 5️⃣ TABLA: 10 principales causas de muerte
# ==============================
st.subheader("📋 10 principales causas de muerte")

# Diccionario manual de nombres de causas
nombres_manual = {
    "I219": "Infarto agudo del miocardio, sin otra especificación",
    "J449": "Enfermedad pulmonar obstructiva crónica",
    "J440": "EPOC con infección aguda de vías respiratorias inferiores",
    "J189": "Neumonía, organismo no especificado",
    "C169": "Tumor maligno del estómago, sin otra especificación",
    "C349": "Tumor maligno de los bronquios o del pulmón",
    "X954": "Agresión con disparo de otras armas de fuego",
    "C509": "Tumor maligno de la mama, sin otra especificación",
    "C61": "Tumor maligno de la próstata",
    "I10": "Hipertensión esencial (primaria)"
}

if "COD_MUERTE" in df.columns:
    causas = df.groupby("COD_MUERTE").size().reset_index(name="Total")
    top10_causas = causas.sort_values("Total", ascending=False).head(10)

    # Integrar nombres manuales
    top10_causas["Nombre causa"] = top10_causas["COD_MUERTE"].map(nombres_manual).fillna("Nombre no disponible")

    # Reordenar columnas y renombrar
    tabla_final = top10_causas[["Nombre causa", "COD_MUERTE", "Total"]]
    tabla_final.columns = ["Causa de muerte", "Código CIE-10", "Número de muertes"]

    # Mostrar tabla ajustada
    st.dataframe(tabla_final)
else:
    st.warning("No se encontró la columna 'COD_MUERTE' en el archivo de mortalidad.")


# ==============================
# 6️⃣ BARRAS APILADAS: Muertes por sexo y departamento
# ==============================
st.subheader("🚻 Comparación de muertes por sexo en cada departamento")

# Mapear códigos de sexo a etiquetas legibles
sexo_map = {1: "Masculino", 2: "Femenino"}
sexo_dep = df_full.copy()
sexo_dep["SEXO"] = sexo_dep["SEXO"].map(sexo_map).fillna("Sin información")

# Agrupar por departamento y sexo
sexo_dep_grouped = sexo_dep.groupby(["DEPARTAMENTO", "SEXO"]).size().reset_index(name="Total")

# Crear gráfico de barras apiladas
fig_barras_apiladas = px.bar(
    sexo_dep_grouped,
    x="DEPARTAMENTO",
    y="Total",
    color="SEXO",
    title="Muertes por sexo y departamento",
    labels={"DEPARTAMENTO": "Departamento", "Total": "Número de muertes", "SEXO": "Sexo"}
)

# Mostrar gráfico con clave única
st.plotly_chart(fig_barras_apiladas, use_container_width=True, key="grafico_sexo_departamento")


# ==============================
# 7️⃣ HISTOGRAMA: Distribución por grupo de edad (mejorado)
# ==============================
st.subheader("📊 Distribución de muertes por grupos de edad")

# Mapeo de grupos etarios a nombres descriptivos
grupo_labels = {
    0: 'Mortalidad neonatal (<1 mes)',
    1: 'Mortalidad neonatal (<1 mes)',
    2: 'Mortalidad neonatal (<1 mes)',
    3: 'Mortalidad neonatal (<1 mes)',
    4: 'Mortalidad neonatal (<1 mes)',
    5: 'Mortalidad infantil (1-11 meses)',
    6: 'Mortalidad infantil (1-11 meses)',
    7: 'Primera infancia (1-4 años)',
    8: 'Primera infancia (1-4 años)',
    9: 'Niñez (5-14 años)',
    10: 'Niñez (5-14 años)',
    11: 'Adolescencia (15-19 años)',
    12: 'Juventud (20-29 años)',
    13: 'Juventud (20-29 años)',
    14: 'Adultez temprana (30-44 años)',
    15: 'Adultez temprana (30-44 años)',
    16: 'Adultez temprana (30-44 años)',
    17: 'Adultez intermedia (45-59 años)',
    18: 'Adultez intermedia (45-59 años)',
    19: 'Adultez intermedia (45-59 años)',
    20: 'Vejez (60-84 años)',
    21: 'Vejez (60-84 años)',
    22: 'Vejez (60-84 años)',
    23: 'Vejez (60-84 años)',
    24: 'Vejez (60-84 años)',
    25: 'Longevidad (85+ años)',
    26: 'Longevidad (85+ años)',
    27: 'Longevidad (85+ años)',
    28: 'Longevidad (85+ años)',
    29: 'Edad desconocida'
}

df["GRUPO_ETARIO_NOMBRE"] = df["GRUPO_EDAD1"].map(grupo_labels).fillna("Sin información")

# Calcular frecuencias
hist_data = df["GRUPO_ETARIO_NOMBRE"].value_counts().reset_index()
hist_data.columns = ["Grupo etario", "Total"]

# Orden lógico de los grupos
orden = [
    'Mortalidad neonatal (<1 mes)',
    'Mortalidad infantil (1-11 meses)',
    'Primera infancia (1-4 años)',
    'Niñez (5-14 años)',
    'Adolescencia (15-19 años)',
    'Juventud (20-29 años)',
    'Adultez temprana (30-44 años)',
    'Adultez intermedia (45-59 años)',
    'Vejez (60-84 años)',
    'Longevidad (85+ años)',
    'Edad desconocida'
]

# Asignar número consecutivo a cada grupo
grupo_numerico = {nombre: i+1 for i, nombre in enumerate(orden)}
hist_data["Grupo_num"] = hist_data["Grupo etario"].map(grupo_numerico)

# Gráfico con números en el eje X
fig_hist = px.bar(
    hist_data,
    x="Grupo_num",
    y="Total",
    color="Grupo etario",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    title="Distribución de muertes por grupo de edad (2019)",
    labels={"Grupo_num": "Grupo etario (número)", "Total": "Número de muertes"}
)

fig_hist.update_layout(
    xaxis_title="Grupo etario (ver leyenda abajo)",
    yaxis_title="Número de muertes",
    xaxis_tickangle=0,
    plot_bgcolor="white",
    showlegend=False
)

st.plotly_chart(fig_hist, use_container_width=True, key="grafico_grupo_etario")

# Leyenda horizontal aclaratoria
st.markdown("""
ℹ️ **Leyenda de grupos etarios:**  
**1**: Mortalidad neonatal (<1 mes)  **2**: Mortalidad infantil (1-11 meses)  **3**: Primera infancia (1-4 años)  **4**: Niñez (5-14 años)  **5**: Adolescencia (15-19 años)  **6**: Juventud (20-29 años)  **7**: Adultez temprana (30-44 años)  **8**: Adultez intermedia (45-59 años)  **9**: Vejez (60-84 años)  **10**: Longevidad (85+ años)  **11**: Edad desconocida
""")
