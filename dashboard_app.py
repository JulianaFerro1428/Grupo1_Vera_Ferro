#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys

sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Ciudad, RegistroClima, MetricasETL

# ==============================
# Configuración de página
# ==============================
st.set_page_config(
    page_title="OpenWeather ETL Dashboard",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Dashboard OpenWeather ETL")
st.markdown("Análisis de datos climáticos almacenados en PostgreSQL")
st.markdown("---")

# ==============================
# Conexión BD
# ==============================
db = SessionLocal()

try:
    # ==============================
    # Consulta con JOIN correcto
    # ==============================
    registros = (
        db.query(RegistroClima, Ciudad.nombre)
        .join(Ciudad, RegistroClima.ciudad_id == Ciudad.id)
        .order_by(RegistroClima.fecha_extraccion.desc())
        .all()
    )

    if not registros:
        st.warning("No hay datos en la base de datos.")
        st.stop()

    # ==============================
    # Convertir a DataFrame
    # ==============================
    data = []
    for registro, ciudad_nombre in registros:
        data.append({
            "Ciudad": ciudad_nombre,
            "Temperatura": registro.temperatura,
            "Sensación Térmica": registro.sensacion_termica,
            "Humedad": registro.humedad,
            "Viento": registro.velocidad_viento,
            "Descripción": registro.descripcion,
            "Fecha": registro.fecha_extraccion
        })

    df = pd.DataFrame(data)

    # ==============================
    # Sidebar filtros
    # ==============================
    st.sidebar.header("🔎 Filtros")

    ciudades = st.sidebar.multiselect(
        "Selecciona ciudades:",
        df["Ciudad"].unique(),
        default=df["Ciudad"].unique()
    )

    df_filtrado = df[df["Ciudad"].isin(ciudades)]

    # ==============================
    # Métricas principales
    # ==============================
    st.subheader("📊 Métricas Principales")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🌡️ Temp. Promedio",
            f"{df_filtrado['Temperatura'].mean():.1f} °C"
        )

    with col2:
        st.metric(
            "💧 Humedad Promedio",
            f"{df_filtrado['Humedad'].mean():.1f} %"
        )

    with col3:
        st.metric(
            "💨 Viento Máximo",
            f"{df_filtrado['Viento'].max():.1f} km/h"
        )

    with col4:
        st.metric(
            "📦 Total Registros",
            len(df_filtrado)
        )

    st.markdown("---")

    # ==============================
    # Gráficas
    # ==============================
    st.subheader("📈 Visualizaciones")

    col1, col2 = st.columns(2)

    with col1:
        fig_temp = px.bar(
            df_filtrado,
            x="Ciudad",
            y="Temperatura",
            color="Temperatura",
            title="Temperatura por Ciudad",
            color_continuous_scale="RdYlBu_r"
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    with col2:
        fig_hum = px.bar(
            df_filtrado,
            x="Ciudad",
            y="Humedad",
            color="Humedad",
            title="Humedad por Ciudad",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_hum, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        fig_scatter = px.scatter(
            df_filtrado,
            x="Temperatura",
            y="Humedad",
            size="Viento",
            color="Ciudad",
            title="Temperatura vs Humedad",
            hover_data=["Descripción"]
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        fig_wind = px.bar(
            df_filtrado,
            x="Ciudad",
            y="Viento",
            color="Viento",
            title="Velocidad del Viento",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_wind, use_container_width=True)

    st.markdown("---")

    # ==============================
    # Tabla detallada
    # ==============================
    st.subheader("📋 Datos Detallados")

    st.dataframe(
        df_filtrado.sort_values("Fecha", ascending=False),
        use_container_width=True
    )

finally:
    db.close()