#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging

# ==============================
# Configuración básica
# ==============================
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    df = pd.read_csv('data/clima.csv')

    if df.empty:
        raise ValueError("El archivo clima.csv está vacío")

    # Convertir viento a km/h
    df['velocidad_viento_kmh'] = df['velocidad_viento'] * 3.6

    # =====================================================
    # 1️⃣ DIAGRAMA DE TORTA (promedios)
    # =====================================================
    plt.figure()

    valores = [
        abs(df['temperatura'].mean()),
        abs(df['sensacion_termica'].mean()),
        abs(df['velocidad_viento_kmh'].mean())
    ]

    etiquetas = ['Temperatura', 'Sensación Térmica', 'Viento (km/h)']

    plt.pie(valores, labels=etiquetas, autopct='%1.1f%%')
    plt.title('Diagrama de Torta - Promedios Climáticos')
    plt.savefig('data/diagrama_torta.png')
    plt.show()

    # =====================================================
    # 2️⃣ MAPA DE CALOR (correlación)
    # =====================================================
    plt.figure()

    matriz = df[['temperatura', 'sensacion_termica', 'velocidad_viento_kmh']].corr()

    plt.imshow(matriz)
    plt.colorbar()

    plt.xticks(range(len(matriz.columns)), matriz.columns, rotation=45)
    plt.yticks(range(len(matriz.columns)), matriz.columns)

    plt.title('Mapa de Calor - Correlación')
    plt.tight_layout()
    plt.savefig('data/mapa_calor.png')
    plt.show()

    # =====================================================
    # 3️⃣ GRÁFICO RADIAL (Radar de promedios)
    # =====================================================
    categorias = ['Temperatura', 'Sensación', 'Viento']
    valores = [
        df['temperatura'].mean(),
        df['sensacion_termica'].mean(),
        df['velocidad_viento_kmh'].mean()
    ]

    valores += valores[:1]  # cerrar figura

    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angulos += angulos[:1]

    plt.figure()
    ax = plt.subplot(111, polar=True)
    ax.plot(angulos, valores)
    ax.fill(angulos, valores, alpha=0.25)

    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias)

    plt.title('Gráfico Radial - Comparación Promedio')
    plt.savefig('data/grafico_radar.png')
    plt.show()

    # =====================================================
    # 4️⃣ DIAGRAMA DE CAJA (distribución real)
    # =====================================================
    plt.figure()

    datos_box = [
        df['temperatura'],
        df['sensacion_termica'],
        df['velocidad_viento_kmh']
    ]

    plt.boxplot(datos_box, labels=['Temperatura', 'Sensación', 'Viento'])

    plt.title('Diagrama de Caja - Distribución')
    plt.ylabel('Valores')
    plt.savefig('data/diagrama_caja.png')
    plt.show()

    logger.info("✅ Gráficos generados correctamente")

except Exception as e:
    logger.error(f"❌ Error en visualización: {str(e)}")