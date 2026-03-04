#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Ciudad, RegistroClima, MetricasETL
from sqlalchemy import func
import pandas as pd

db = SessionLocal()


# ==========================================
# 1️⃣ Temperatura promedio por ciudad
# ==========================================
def temperatura_promedio_por_ciudad():
    registros = db.query(
        Ciudad.nombre,
        func.avg(RegistroClima.temperatura).label("temp_promedio")
    ).join(RegistroClima).group_by(Ciudad.nombre).all()

    df = pd.DataFrame(registros, columns=["Ciudad", "Temperatura Promedio °C"])

    print("\n📊 TEMPERATURA PROMEDIO POR CIUDAD")
    print(df.to_string(index=False))


# ==========================================
# 2️⃣ Ciudad con mayor humedad registrada
# ==========================================
def ciudad_mas_humeda():
    registro = db.query(
        Ciudad.nombre,
        RegistroClima.humedad,
        RegistroClima.fecha_extraccion
    ).join(Ciudad).order_by(
        RegistroClima.humedad.desc()
    ).first()

    if registro:
        print("\n💧 CIUDAD MÁS HÚMEDA REGISTRADA")
        print(f"{registro.nombre} - {registro.humedad}% ({registro.fecha_extraccion})")


# ==========================================
# 3️⃣ Viento más fuerte registrado
# ==========================================
def viento_maximo():
    registro = db.query(
        Ciudad.nombre,
        RegistroClima.velocidad_viento
    ).join(Ciudad).order_by(
        RegistroClima.velocidad_viento.desc()
    ).first()

    if registro:
        print("\n💨 VIENTO MÁS FUERTE REGISTRADO")
        print(f"{registro.nombre} - {registro.velocidad_viento} m/s")


# ==========================================
# 4️⃣ Presión promedio global
# ==========================================
def presion_promedio_global():
    promedio = db.query(
        func.avg(RegistroClima.presion)
    ).scalar()

    if promedio:
        print("\n🌡️ PRESIÓN PROMEDIO GLOBAL")
        print(f"{promedio:.2f} hPa")


# ==========================================
# 5️⃣ Últimas ejecuciones del ETL
# ==========================================
def ultimas_metricas():
    metricas = db.query(MetricasETL).order_by(
        MetricasETL.fecha_ejecucion.desc()
    ).limit(5).all()

    print("\n📈 ÚLTIMAS 5 EJECUCIONES ETL")
    for m in metricas:
        print(
            f"{m.fecha_ejecucion} | {m.estado} | "
            f"Guardados: {m.registros_guardados} | "
            f"Fallidos: {m.registros_fallidos} | "
            f"Tiempo: {m.tiempo_ejecucion_segundos:.2f}s"
        )


# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("📊 ANÁLISIS DE DATOS - OPENWEATHER ETL")
        print("="*60)

        temperatura_promedio_por_ciudad()
        ciudad_mas_humeda()
        viento_maximo()
        presion_promedio_global()
        ultimas_metricas()

        print("\n" + "="*60 + "\n")

    finally:
        db.close()