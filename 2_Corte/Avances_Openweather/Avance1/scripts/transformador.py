#!/usr/bin/env python3

import pandas as pd
import os
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class OpenWeatherTransformador:

    def __init__(self, input_json='data/clima_raw.json'):
        self.input_json = input_json
        self.df = None

    # ======================================
    # CARGA DESDE JSON
    # ======================================
    def cargar_datos(self):
        if not os.path.exists(self.input_json):
            raise FileNotFoundError("Ejecuta primero extractor.py")

        with open(self.input_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 🔥 convierte JSON a tabla
        self.df = pd.json_normalize(data)

        logger.info(f"📂 Datos cargados: {len(self.df)} registros")

        return self

    # ======================================
    # TRANSFORMACIÓN
    # ======================================
    def transformar_estructura(self):

        self.df = self.df.rename(columns={
            "name": "ciudad",
            "sys.country": "pais",
            "coord.lat": "latitud",
            "coord.lon": "longitud",
            "main.temp": "temperatura",
            "main.feels_like": "sensacion_termica",
            "main.humidity": "humedad",
            "main.pressure": "presion",
            "wind.speed": "velocidad_viento",
            "weather.0.description": "descripcion"
        })

        columnas = [
            "ciudad", "pais", "latitud", "longitud",
            "temperatura", "sensacion_termica",
            "humedad", "presion", "velocidad_viento",
            "descripcion"
        ]

        # 🔥 evita errores si falta alguna columna
        columnas_existentes = [col for col in columnas if col in self.df.columns]

        self.df = self.df[columnas_existentes]

        logger.info("🔄 Estructura transformada correctamente")

        return self

    # ======================================
    # LIMPIEZA
    # ======================================
    def limpiar_datos(self):
        self.df.drop_duplicates(inplace=True)

        self.df.fillna({
            'temperatura': 0.0,
            'sensacion_termica': 0.0,
            'humedad': 0,
            'presion': 0,
            'velocidad_viento': 0.0,
            'descripcion': 'Sin descripción'
        }, inplace=True)

        logger.info("🧹 Datos limpiados")
        return self

    # ======================================
    # ENRIQUECIMIENTO
    # ======================================
    def enriquecer_datos(self):

        self.df['categoria_temperatura'] = self.df['temperatura'].apply(
            lambda t: 'Frío' if t < 10 else 'Templado' if t < 20 else 'Cálido' if t < 30 else 'Caluroso'
        )

        self.df['diferencial_termico'] = (
            self.df['temperatura'] - self.df['sensacion_termica']
        )

        self.df['fecha_procesamiento'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        logger.info("✨ Datos enriquecidos")
        return self

    # ======================================
    # GUARDAR
    # ======================================
    def guardar_datos(self):
        self.df.to_csv("data/clima_transformado.csv", index=False)
        logger.info("💾 Datos transformados guardados")
        return self.df


# ======================================
# MAIN
# ======================================
if __name__ == "__main__":
    transformador = OpenWeatherTransformador()

    (transformador
     .cargar_datos()
     .transformar_estructura()
     .limpiar_datos()
     .enriquecer_datos()
     .guardar_datos())