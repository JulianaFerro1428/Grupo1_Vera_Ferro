#!/usr/bin/env python3

import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# =====================================================
# CONFIGURACIÓN
# =====================================================

os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/etl.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# =====================================================
# CARGAR DATOS
# =====================================================

try:

    df = pd.read_csv("data/clima.csv")

    if df.empty:
        raise ValueError("El archivo clima.csv está vacío")

    # convertir viento a km/h
    df["velocidad_viento_kmh"] = df["velocidad_viento"] * 3.6


    # =====================================================
    # DIAGRAMA DE TORTA
    # =====================================================

    plt.figure()

    valores = [
        abs(df["temperatura"].mean()),
        abs(df["sensacion_termica"].mean()),
        abs(df["velocidad_viento_kmh"].mean())
    ]

    etiquetas = [
        "Temperatura",
        "Sensación térmica",
        "Viento (km/h)"
    ]

    plt.pie(valores, labels=etiquetas, autopct="%1.1f%%")
    plt.title("Diagrama de Torta - Promedios Climáticos")

    plt.savefig("data/diagrama_torta.png")
    plt.close()


    # =====================================================
    # MAPA DE CALOR (CORRELACIÓN)
    # =====================================================

    plt.figure()

    matriz = df[
        ["temperatura", "sensacion_termica", "velocidad_viento_kmh"]
    ].corr()

    plt.imshow(matriz, cmap="coolwarm")
    plt.colorbar()

    plt.xticks(range(len(matriz.columns)), matriz.columns, rotation=45)
    plt.yticks(range(len(matriz.columns)), matriz.columns)

    plt.title("Mapa de Calor - Correlación")

    plt.tight_layout()
    plt.savefig("data/mapa_calor.png")
    plt.close()


    # =====================================================
    # GRÁFICO RADIAL (RADAR)
    # =====================================================

    categorias = ["Temperatura", "Sensación", "Viento"]

    valores = [
        df["temperatura"].mean(),
        df["sensacion_termica"].mean(),
        df["velocidad_viento_kmh"].mean()
    ]

    valores += valores[:1]

    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angulos += angulos[:1]

    plt.figure()

    ax = plt.subplot(111, polar=True)

    ax.plot(angulos, valores)
    ax.fill(angulos, valores, alpha=0.25)

    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias)

    plt.title("Gráfico Radial - Comparación Promedio")

    plt.savefig("data/grafico_radar.png")
    plt.close()


    # =====================================================
    # DIAGRAMA DE CAJA (BOXPLOT)
    # =====================================================

    plt.figure()

    datos_box = [
        df["temperatura"],
        df["sensacion_termica"],
        df["velocidad_viento_kmh"]
    ]

    plt.boxplot(
        datos_box,
        labels=["Temperatura", "Sensación", "Viento"],
        patch_artist=True
    )

    plt.title("Diagrama de Caja - Distribución")
    plt.ylabel("Valores")

    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.savefig("data/diagrama_caja.png")
    plt.close()


    # =====================================================
    # HISTOGRAMA
    # =====================================================

    plt.figure()

    plt.hist(
        df["temperatura"],
        bins=20,
        edgecolor="black",
        linewidth=1,
        alpha=0.8
    )

    plt.title("Histograma - Distribución de Temperaturas")
    plt.xlabel("Temperatura")
    plt.ylabel("Frecuencia")

    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.savefig("data/histograma_temperatura.png")
    plt.close()


    # =====================================================
    # SCATTER PLOT
    # =====================================================

    plt.figure()

    plt.scatter(
        df["temperatura"],
        df["humedad"],
        alpha=0.6
    )

    plt.xlabel("Temperatura")
    plt.ylabel("Humedad")

    plt.title("Relación entre Temperatura y Humedad")

    plt.grid(True, linestyle="--", alpha=0.5)

    plt.savefig("data/scatter_temperatura_humedad.png")
    plt.close()


    # =====================================================
    # FIN
    # =====================================================

    logger.info("✅ Gráficos generados correctamente")
    logger.info("📊 Archivos guardados en la carpeta data/")

except Exception as e:
    logger.error(f"❌ Error en visualización: {str(e)}")