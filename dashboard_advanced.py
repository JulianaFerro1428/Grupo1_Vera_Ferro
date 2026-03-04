#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from sqlalchemy import func
import sys

sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Ciudad, RegistroClima, MetricasETL

# ======================================
# Configuración página
# ======================================
st.set_page_config(
    page_title="OpenWeather ETL - Dashboard Avanzado",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 OpenWeather ETL - Dashboard Avanzado")
st.markdown("---")

db = SessionLocal()

# ======================================
# TABS PRINCIPALES
# ======================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Vista General",
    "📈 Histórico",
    "🔎 Análisis Estadístico",
    "⚙️ Métricas ETL"
])

# ======================================
# TAB 1 - VISTA GENERAL
# ======================================
with tab1:

    st.subheader("📊 Estado Actual del Sistema")

    col1, col2, col3 = st.columns(3)

    with col1:
        ciudades_count = db.query(func.count(Ciudad.id)).scalar() or 0
        st.metric("🏙️ Ciudades Registradas", ciudades_count)

    with col2:
        registros_count = db.query(func.count(RegistroClima.id)).scalar() or 0
        st.metric("📊 Registros Totales", registros_count)

    with col3:
        ultima_fecha = db.query(func.max(RegistroClima.fecha_extraccion)).scalar()
        if ultima_fecha:
            st.metric("⏰ Última Actualización", ultima_fecha.strftime("%Y-%m-%d %H:%M"))
        else:
            st.metric("⏰ Última Actualización", "Sin datos")

    st.markdown("---")

    # Obtener último registro por ciudad (más correcto que distinct simple)
    subquery = (
        db.query(
            RegistroClima.ciudad_id,
            func.max(RegistroClima.fecha_extraccion).label("max_fecha")
        )
        .group_by(RegistroClima.ciudad_id)
        .subquery()
    )

    registros_actuales = (
        db.query(
            Ciudad.nombre,
            RegistroClima.temperatura,
            RegistroClima.humedad,
            RegistroClima.velocidad_viento,
            RegistroClima.descripcion
        )
        .join(RegistroClima, Ciudad.id == RegistroClima.ciudad_id)
        .join(subquery,
              (RegistroClima.ciudad_id == subquery.c.ciudad_id) &
              (RegistroClima.fecha_extraccion == subquery.c.max_fecha))
        .all()
    )

    if registros_actuales:
        df_actual = pd.DataFrame(registros_actuales, columns=[
            "Ciudad", "Temperatura", "Humedad", "Viento", "Descripción"
        ])

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                df_actual,
                x="Ciudad",
                y="Temperatura",
                color="Temperatura",
                title="🌡️ Temperatura Actual",
                color_continuous_scale="RdYlBu_r"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                df_actual,
                x="Ciudad",
                y="Humedad",
                color="Humedad",
                title="💧 Humedad Actual",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.dataframe(df_actual, use_container_width=True)

    else:
        st.warning("No hay datos registrados aún.")

# ======================================
# TAB 2 - HISTÓRICO
# ======================================
with tab2:

    st.subheader("📈 Análisis Histórico")

    col1, col2 = st.columns(2)

    with col1:
        fecha_inicio = st.date_input(
            "Desde",
            value=datetime.now() - timedelta(days=7)
        )

    with col2:
        fecha_fin = st.date_input(
            "Hasta",
            value=datetime.now()
        )

    registros_historicos = (
        db.query(
            RegistroClima.fecha_extraccion,
            Ciudad.nombre,
            RegistroClima.temperatura,
            RegistroClima.humedad,
            RegistroClima.velocidad_viento
        )
        .join(Ciudad)
        .filter(
            RegistroClima.fecha_extraccion >= fecha_inicio,
            RegistroClima.fecha_extraccion <= fecha_fin
        )
        .all()
    )

    if registros_historicos:

        df_historico = pd.DataFrame(registros_historicos, columns=[
            "Fecha", "Ciudad", "Temperatura", "Humedad", "Viento"
        ])

        fig = px.line(
            df_historico,
            x="Fecha",
            y="Temperatura",
            color="Ciudad",
            markers=True,
            title="🌡️ Evolución de Temperatura"
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")
        st.dataframe(df_historico, use_container_width=True)

    else:
        st.warning("No hay datos en ese rango de fechas.")

# ======================================
# TAB 3 - ANÁLISIS ESTADÍSTICO
# ======================================
with tab3:

    st.subheader("🔎 Estadísticas por Ciudad")

    ciudades = db.query(Ciudad).all()

    for ciudad in ciudades:

        with st.expander(f"📍 {ciudad.nombre}"):

            registros = db.query(RegistroClima).filter_by(
                ciudad_id=ciudad.id
            ).all()

            if registros:

                temps = [r.temperatura for r in registros]
                humeds = [r.humedad for r in registros]
                vientos = [r.velocidad_viento for r in registros]

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("🌡️ Temp Prom.", f"{sum(temps)/len(temps):.1f}°C")

                with col2:
                    st.metric("💧 Humedad Prom.", f"{sum(humeds)/len(humeds):.1f}%")

                with col3:
                    st.metric("💨 Viento Prom.", f"{sum(vientos)/len(vientos):.1f} km/h")

                with col4:
                    st.metric("📊 Total Registros", len(registros))

# ======================================
# TAB 4 - MÉTRICAS ETL
# ======================================
with tab4:

    st.subheader("⚙️ Métricas de Ejecución ETL")

    metricas = (
        db.query(MetricasETL)
        .order_by(MetricasETL.fecha_ejecucion.desc())
        .limit(20)
        .all()
    )

    if metricas:

        data = []
        for m in metricas:
            data.append({
                "Fecha": m.fecha_ejecucion,
                "Estado": m.estado,
                "Extraídos": m.registros_extraidos,
                "Guardados": m.registros_guardados,
                "Fallidos": m.registros_fallidos,
                "Tiempo (s)": m.tiempo_ejecucion_segundos
            })

        df_metricas = pd.DataFrame(data)

        st.dataframe(df_metricas, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                df_metricas,
                x="Fecha",
                y="Guardados",
                color="Estado",
                title="📊 Registros Guardados por Ejecución"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.scatter(
                df_metricas,
                x="Fecha",
                y="Tiempo (s)",
                size="Guardados",
                color="Estado",
                title="⏱️ Duración de Ejecuciones"
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No hay métricas registradas aún.")

db.close()