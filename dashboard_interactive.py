#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from sqlalchemy import and_

import sys
sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Ciudad, RegistroClima, MetricasETL

st.set_page_config(
    page_title="Dashboard Interactivo - Clima",
    page_icon="🌦️",
    layout="wide"
)

st.title("🌦️ Dashboard Interactivo - Proyecto Clima")

db = SessionLocal()

# ==============================
# SIDEBAR CONTROLES
# ==============================

st.sidebar.header("🔧 Filtros")

ciudades_disponibles = [c.nombre for c in db.query(Ciudad).all()]

ciudades_seleccionadas = st.sidebar.multiselect(
    "🏙️ Ciudades",
    options=ciudades_disponibles,
    default=ciudades_disponibles
)

fecha_inicio = st.sidebar.date_input(
    "📅 Desde",
    value=datetime.now() - timedelta(days=30)
)

fecha_fin = st.sidebar.date_input(
    "📅 Hasta",
    value=datetime.now()
)

if fecha_inicio > fecha_fin:
    st.error("La fecha inicial no puede ser mayor que la final")
    st.stop()

fecha_inicio_dt = datetime.combine(fecha_inicio, datetime.min.time())
fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time())

# ==============================
# CONSULTA FILTRADA
# ==============================

registros = db.query(
    RegistroClima,
    Ciudad.nombre,
    Ciudad.pais
).join(Ciudad).filter(
    and_(
        Ciudad.nombre.in_(ciudades_seleccionadas),
        RegistroClima.fecha_extraccion >= fecha_inicio_dt,
        RegistroClima.fecha_extraccion <= fecha_fin_dt
    )
).all()

data = []

for registro, ciudad, pais in registros:
    data.append({
        "Ciudad": ciudad,
        "País": pais,
        "Temperatura": registro.temperatura,
        "Humedad": registro.humedad,
        "Viento": registro.velocidad_viento,
        "Descripción": registro.descripcion,
        "Fecha": registro.fecha_extraccion
    })

df = pd.DataFrame(data)

# ==============================
# CONTENIDO PRINCIPAL
# ==============================

if not df.empty:

    # ================= KPIs =================
    st.subheader("📊 Indicadores Clave")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("🌡️ Temp Máx", f"{df['Temperatura'].max():.1f}°C")
    col2.metric("❄️ Temp Mín", f"{df['Temperatura'].min():.1f}°C")
    col3.metric("🌡️ Temp Prom", f"{df['Temperatura'].mean():.1f}°C")
    col4.metric("💧 Humedad Prom", f"{df['Humedad'].mean():.1f}%")
    col5.metric("📊 Registros", len(df))

    st.markdown("---")

    # ================= BOX PLOT =================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribución de Temperaturas")
        fig = px.box(
            df,
            x="Ciudad",
            y="Temperatura",
            color="Ciudad"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Promedio de Humedad por Ciudad")
        humedad = df.groupby("Ciudad")["Humedad"].mean().reset_index()

        fig = px.bar(
            humedad,
            x="Ciudad",
            y="Humedad",
            color="Humedad",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ================= LÍNEA TEMPORAL =================
    st.subheader("📈 Evolución Temporal de la Temperatura")

    df["Fecha"] = pd.to_datetime(df["Fecha"])

    temp_tiempo = df.groupby(["Fecha", "Ciudad"])["Temperatura"] \
                    .mean().reset_index()

    fig = px.line(
        temp_tiempo,
        x="Fecha",
        y="Temperatura",
        color="Ciudad",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ================= ESTADO ETL RESUMIDO =================
    ultima_etl = db.query(MetricasETL) \
                    .order_by(MetricasETL.fecha_ejecucion.desc()) \
                    .first()

    if ultima_etl:
        st.subheader("⚙️ Última Ejecución ETL")

        col1, col2, col3 = st.columns(3)

        col1.metric("📥 Registros Insertados", ultima_etl.registros_guardados)
        col2.metric("⏱️ Duración (seg)", ultima_etl.tiempo_ejecucion_segundos)
        col3.metric("Estado", ultima_etl.estado)

        st.markdown("---")

    # ================= TABLA =================
    st.subheader("📋 Datos Detallados")

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button(
        "⬇️ Descargar CSV",
        csv,
        file_name="datos_clima.csv",
        mime="text/csv"
    )

else:
    st.warning("No hay datos que coincidan con los filtros seleccionados.")

db.close()