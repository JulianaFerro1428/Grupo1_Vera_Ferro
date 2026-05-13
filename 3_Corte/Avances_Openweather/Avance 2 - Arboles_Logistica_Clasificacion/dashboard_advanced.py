#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
import sys

sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Ciudad, RegistroClima

# ==============================
# CONFIGURACIÓN
# ==============================
st.set_page_config(
    page_title="OpenWeather ETL PRO",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Dashboard OpenWeather ETL - PRO")
st.markdown("---")

db = SessionLocal()

# ==============================
# CONSULTA PRINCIPAL
# ==============================
registros = (
    db.query(
        Ciudad.nombre,
        RegistroClima.temperatura,
        RegistroClima.humedad,
        RegistroClima.velocidad_viento,
        RegistroClima.descripcion
    )
    .join(Ciudad)
    .all()
)

if not registros:
    st.warning("No hay datos en la base de datos.")
    st.stop()

df = pd.DataFrame(registros, columns=[
    "Ciudad", "Temperatura", "Humedad", "Viento", "Descripción"
])

# ==============================
# AGRUPACIÓN GLOBAL 🔥
# ==============================
df_grouped = df.groupby("Ciudad").agg({
    "Temperatura": "mean",
    "Humedad": "mean",
    "Viento": "mean"
}).reset_index()

# ==============================
# TOP 15 (CLAVE 🔥)
# ==============================
df_top_temp = df_grouped.sort_values("Temperatura", ascending=False).head(15)
df_top_hum = df_grouped.sort_values("Humedad", ascending=False).head(15)
df_top_wind = df_grouped.sort_values("Viento", ascending=False).head(15)

# ==============================
# MÉTRICAS
# ==============================
st.subheader("📊 Métricas Generales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🌡️ Temp Promedio", f"{df['Temperatura'].mean():.1f} °C")

with col2:
    st.metric("💧 Humedad Promedio", f"{df['Humedad'].mean():.1f} %")

with col3:
    st.metric("💨 Viento Promedio", f"{df['Viento'].mean():.1f} km/h")

with col4:
    st.metric("📦 Registros", len(df))

st.markdown("---")

# ==============================
# GRÁFICAS PRINCIPALES
# ==============================
st.subheader("📈 Top 15 Ciudades")

col1, col2 = st.columns(2)

# 🌡️ Temperatura
with col1:
    fig = px.bar(
        df_top_temp.sort_values("Temperatura"),
        x="Ciudad",
        y="Temperatura",
        color="Temperatura",
        title="🔥 Top 15 Ciudades más Calientes"
    )
    st.plotly_chart(fig, use_container_width=True)

# 💧 Humedad
with col2:
    fig = px.bar(
        df_top_hum.sort_values("Humedad"),
        x="Ciudad",
        y="Humedad",
        color="Humedad",
        title="💧 Top 15 Ciudades más Húmedas"
    )
    st.plotly_chart(fig, use_container_width=True)

# 💨 Viento
fig = px.bar(
    df_top_wind.sort_values("Viento"),
    x="Ciudad",
    y="Viento",
    color="Viento",
    title="💨 Top 15 Ciudades con Mayor Viento"
)
st.plotly_chart(fig, use_container_width=True)

# ==============================
# RELACIONES (USANDO TOP 🔥)
# ==============================
st.subheader("🔎 Relaciones entre Variables")

col1, col2 = st.columns(2)

with col1:
    fig = px.scatter(
        df_top_temp,
        x="Temperatura",
        y="Humedad",
        size="Viento",
        color="Ciudad",
        title="🌡️ vs 💧 Temperatura vs Humedad"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.scatter(
        df_top_temp,
        x="Viento",
        y="Temperatura",
        size="Humedad",
        color="Ciudad",
        title="💨 vs 🌡️ Viento vs Temperatura"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==============================
# DISTRIBUCIONES
# ==============================
st.subheader("📊 Distribuciones Globales")

col1, col2, col3 = st.columns(3)

with col1:
    fig = px.histogram(df, x="Temperatura", title="Distribución Temperatura")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(df, x="Humedad", title="Distribución Humedad")
    st.plotly_chart(fig, use_container_width=True)

with col3:
    fig = px.histogram(df, x="Viento", title="Distribución Viento")
    st.plotly_chart(fig, use_container_width=True)

# ==============================
# TABLA FINAL (TOP 15)
# ==============================
st.subheader("📋 Top 15 Ciudades (Resumen)")

st.dataframe(df_top_temp, use_container_width=True)

db.close()