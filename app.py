import streamlit as st
import pandas as pd

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(page_title="Spotify Music Analytics", layout="wide")

st.title("🎧 Spotify Music Analytics")
st.caption("Explora tendencias, artistas y popularidad")

# =========================
# CARGAR DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("spotify.csv")
    return df

df = load_data()

# =========================
# LIMPIAR COLUMNAS
# =========================
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
# Ajustar nombres si es necesario
# Asegúrate que tu CSV tenga: artist_name, track_name, album_type, track_popularity, artist_popularity, track_duration_min, album_release_date



# =========================
# CONVERTIR FECHAS
# =========================
df["album_release_date"] = pd.to_datetime(df["album_release_date"])
df["release_year"] = df["album_release_date"].dt.year
df["year_month"] = df["album_release_date"].dt.to_period("M").dt.to_timestamp()

# =========================
# SIDEBAR - FILTROS
# =========================
st.sidebar.header("🎛 Filtros")

artistas = st.sidebar.multiselect(
    "Artista",
    sorted(df["artist_name"].dropna().unique()),
    default=sorted(df["artist_name"].dropna().unique())
)

album_type = st.sidebar.multiselect(
    "Tipo de Álbum",
    sorted(df["album_type"].dropna().unique()),
    default=sorted(df["album_type"].dropna().unique())
)

pop_range = st.sidebar.slider(
    "Rango de Popularidad del Track",
    0, 100, (0, 100)
)

anio_range = st.sidebar.slider(
    "Año de Lanzamiento",
    int(df["release_year"].min()),
    int(df["release_year"].max()),
    (int(df["release_year"].min()), int(df["release_year"].max()))
)

# =========================
# APLICAR FILTROS
# =========================
df_filtrado = df[
    (df["artist_name"].isin(artistas)) &
    (df["album_type"].isin(album_type)) &
    (df["track_popularity"].between(pop_range[0], pop_range[1])) &
    (df["release_year"].between(anio_range[0], anio_range[1]))
]

# =========================
# TABS PRINCIPALES
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["📊 KPIs", "📈 Gráficos", "🎧 Perfil Artista", "📋 Tabla"])

# =====================================================
# TAB 1 - KPIs
# =====================================================
with tab1:
    st.subheader("📊 Métricas Principales")
    col1, col2, col3, col4 = st.columns(4)

    avg_pop = round(df_filtrado["track_popularity"].mean(), 2)
    total_artistas = df_filtrado["artist_name"].nunique()
    avg_duration = round(df_filtrado["track_duration_min"].mean(), 2)
    total_canciones = len(df_filtrado)

    col1.metric("⭐ Popularidad Promedio (Track)", avg_pop)
    col2.metric("🎤 Total Artistas", total_artistas)
    col3.metric("⏱ Duración Promedio", f"{avg_duration} min")
    col4.metric("🎵 Total Canciones", total_canciones)

# =====================================================
# TAB 2 - GRÁFICOS
# =====================================================
with tab2:
     
    st.subheader("🔥 Top 10 Artistas Más Populares")
 
    top_artistas = (
        df_filtrado.groupby("artist_name")["artist_popularity"]
        .mean()
        .sort_values(ascending=True)  # Ascendente para barra horizontal
        .tail(10)
        .reset_index()
    )
 
    st.bar_chart(
        top_artistas,
        x="artist_popularity",
        y="artist_name",
        horizontal=True
    )
    st.subheader("⏱ Popularidad Promedio por Rango de Duración")
 
    if len(df_filtrado) > 0:
 
        df_filtrado = df_filtrado.copy()
 
        df_filtrado["duracion_grupo"] = pd.cut(
            df_filtrado["track_duration_min"],
            bins=[0, 3, 4, 5, float("inf")],
            labels=["0-3 min", "3-4 min", "4-5 min", "5+ min"]
        )
 
        duracion_pop = (
            df_filtrado
            .groupby("duracion_grupo")["artist_popularity"]
            .mean()
            .reset_index()
        )
 
        st.bar_chart(
            duracion_pop,
            x="duracion_grupo",
            y="artist_popularity"
        )
 

    st.subheader("Popularidad promedio por año según tipo de álbum")
    promedio_anual = df_filtrado.groupby(['release_year', 'album_type'])['track_popularity'].mean().unstack()
    st.bar_chart(promedio_anual)

 

# =====================================================
# TAB 3 - PERFIL DETALLADO DEL ARTISTA
# =====================================================
with tab3:
    st.header("🎧 Perfil Detallado del Artista")
    if len(df_filtrado) > 0:
        artista_perfil = st.selectbox(
            "Selecciona un artista",
            sorted(df_filtrado["artist_name"].unique())
        )

        df_artista = df_filtrado[df_filtrado["artist_name"] == artista_perfil]

        # Métricas del artista
        popularidad_prom = round(df_artista["artist_popularity"].mean(), 2)
        num_canciones = df_artista["track_name"].nunique()
        album_frecuente = df_artista["album_type"].mode()[0]

        cancion_top = df_artista.loc[df_artista["track_popularity"].idxmax()]
        nombre_cancion_top = cancion_top["track_name"]
        popularidad_top = cancion_top["track_popularity"]

        col1, col2, col3 = st.columns(3)
        col1.metric("⭐ Popularidad Promedio (Artista)", popularidad_prom)
        col2.metric("🎵 Número de Canciones", num_canciones)
        col3.metric("💿 Álbum Más Frecuente", album_frecuente)

        st.subheader("🎶 Canción Más Popular")
        st.success(f"{nombre_cancion_top} — Popularidad: {popularidad_top}")

# =====================================================
# TAB 4 - TABLA
# =====================================================
with tab4:
   
    st.subheader("📄 Lista de canciones")
 
    tabla = df_filtrado[[
        "album_release_date",
        "artist_name",
        "artist_popularity",
        "track_duration_min"
    ]].copy()
 
    tabla.columns = [
        "Fecha Lanzamiento",
        "Artista",
        "Popularidad",
        "Duración (min)"
    ]
 
    st.dataframe(tabla, use_container_width=True)
 