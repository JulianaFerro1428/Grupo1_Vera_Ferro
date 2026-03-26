#!/usr/bin/env python3
"""
dashboard_interactive.py — Dashboard interactivo con control total de filtros.
Ejecutar: streamlit run dashboard_interactive.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import sys
sys.path.insert(0, '.')

from scripts.database import SessionLocal, DB_HOST
from scripts.models import Ciudad, RegistroClima

# ── Configuración de página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Interactivo",
    page_icon="🎛️",
    layout="wide",
)

# CSS personalizado
st.markdown("""
<style>
.metric-box {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
.stMetric {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 12px;
    border-left: 4px solid #2a5298;
}
</style>
""", unsafe_allow_html=True)

st.title("🎛️ Dashboard Interactivo — Control Total")

# Verifica configuración
if DB_HOST == "localhost":
    st.error("🔐 Base de datos no configurada.")
    st.stop()

db = SessionLocal()

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("### 🔧 Controles")

ciudades_disponibles = [c.nombre for c in db.query(Ciudad).order_by(Ciudad.nombre).all()]

ciudades_seleccionadas = st.sidebar.multiselect(
    "🏙️ Ciudades",
    options=ciudades_disponibles,
    default=ciudades_disponibles,
)

col1, col2 = st.sidebar.columns(2)
with col1:
    fecha_inicio = st.date_input("Desde", value=datetime.now() - timedelta(days=30))
with col2:
    fecha_fin = st.date_input("Hasta", value=datetime.now())

temp_min_db = db.query(func.min(RegistroClima.temperatura)).scalar() or -10
temp_max_db = db.query(func.max(RegistroClima.temperatura)).scalar() or 50

temp_rango = st.sidebar.slider(
    "🌡️ Temperatura",
    int(temp_min_db)-1,
    int(temp_max_db)+1,
    (int(temp_min_db)-1, int(temp_max_db)+1)
)

# ── Consulta ───────────────────────────────────────────────────────────────────
registros = (
    db.query(RegistroClima, Ciudad.nombre, Ciudad.pais)
    .join(Ciudad)
    .filter(
        and_(
            Ciudad.nombre.in_(ciudades_seleccionadas) if ciudades_seleccionadas else True,
            RegistroClima.fecha_extraccion >= fecha_inicio,
            RegistroClima.fecha_extraccion <= fecha_fin,
            RegistroClima.temperatura >= temp_rango[0],
            RegistroClima.temperatura <= temp_rango[1],
        )
    )
    .all()
)

@st.cache_data
def construir_df(_registros):
    data = []
    for r, ciudad, pais in _registros:
        data.append({
            "Ciudad": ciudad,
            "País": pais,
            "Temperatura": r.temperatura,
            "Sensación": r.sensacion_termica,
            "Humedad": r.humedad,
            "Viento": r.velocidad_viento,
            "Descripción": r.descripcion,
            "Fecha": r.fecha_extraccion,
        })
    return pd.DataFrame(data)

df = construir_df(registros) if registros else pd.DataFrame()

# ── UI ─────────────────────────────────────────────────────────────────────────
if not df.empty:
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    st.markdown("### 📊 Indicadores")
    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric("Registros", len(df))
    c2.metric("Temp Prom", f"{df['Temperatura'].mean():.1f}°C")
    c3.metric("Temp Max", f"{df['Temperatura'].max():.1f}°C")
    c4.metric("Humedad", f"{df['Humedad'].mean():.1f}%")
    c5.metric("Viento Max", f"{df['Viento'].max():.0f}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.box(df, x="Ciudad", y="Temperatura", color="Ciudad")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        hum = df.groupby("Ciudad")["Humedad"].mean().reset_index()
        fig = px.bar(hum, x="Ciudad", y="Humedad")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📈 Evolución")
    temp = df.groupby([pd.Grouper(key="Fecha", freq="6h"), "Ciudad"])["Temperatura"].mean().reset_index()
    fig = px.line(temp, x="Fecha", y="Temperatura", color="Ciudad")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔬 Scatter")
    fig = px.scatter(df, x="Temperatura", y="Humedad", size="Viento", color="Ciudad")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Datos")

    mostrar = st.checkbox("Mostrar todos")
    columnas = st.multiselect("Columnas", df.columns, default=df.columns.tolist())

    vista = df[columnas]

    if mostrar:
        st.dataframe(vista, use_container_width=True, height=600)
    else:
        st.dataframe(vista.head(100), use_container_width=True, height=400)

    st.download_button(
        "Descargar CSV",
        df.to_csv(index=False),
        file_name="datos.csv"
    )

else:
    st.warning("No hay datos con esos filtros")

db.close()