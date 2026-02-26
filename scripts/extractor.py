#!/usr/bin/env python3
import os
import requests
import json
import random
import time
from datetime import datetime
from dotenv import load_dotenv
import logging
import pandas as pd

# ==============================
# Cargar variables
# ==============================
load_dotenv()

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


class OpenWeatherExtractor:

    def __init__(self, total_ciudades=100):
        self.api_key = os.getenv("API_KEY")
        self.base_url = os.getenv("OPENWEATHER_URL")
        self.total_ciudades = total_ciudades

        if not self.api_key:
            raise ValueError("API_KEY no configurada en .env")

        if not self.base_url:
            raise ValueError("OPENWEATHER_URL no configurada en .env")

    def generar_coordenadas(self):
        lat = random.uniform(-60, 75)   # evitamos polos extremos
        lon = random.uniform(-180, 180)
        return lat, lon

    def extraer_clima(self, lat, lon):
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "lang": "es"
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"❌ Error en coordenadas {lat},{lon}: {str(e)}")
            return None

    def procesar_respuesta(self, data):
        try:
            ciudad = data.get("name")

            if not ciudad:
                return None  # ignoramos océanos

            return {
                "ciudad": ciudad,
                "pais": data.get("sys", {}).get("country"),
                "latitud": data.get("coord", {}).get("lat"),
                "longitud": data.get("coord", {}).get("lon"),
                "temperatura": data.get("main", {}).get("temp"),
                "sensacion_termica": data.get("main", {}).get("feels_like"),
                "humedad": data.get("main", {}).get("humidity"),
                "presion": data.get("main", {}).get("pressure"),
                "velocidad_viento": data.get("wind", {}).get("speed"),
                "descripcion": data.get("weather", [{}])[0].get("description"),
                "fecha_extraccion": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error procesando datos: {str(e)}")
            return None

    def ejecutar_extraccion(self):
        ciudades_unicas = set()
        datos = []

        logger.info(f"Generando {self.total_ciudades} ciudades únicas...")

        while len(ciudades_unicas) < self.total_ciudades:

            lat, lon = self.generar_coordenadas()
            response = self.extraer_clima(lat, lon)

            if response:
                procesado = self.procesar_respuesta(response)

                if procesado:
                    ciudad = procesado["ciudad"]

                    if ciudad not in ciudades_unicas:
                        ciudades_unicas.add(ciudad)
                        datos.append(procesado)
                        logger.info(f"✅ {ciudad} agregada ({len(ciudades_unicas)}/{self.total_ciudades})")

            time.sleep(1)  # evitar rate limit

        return datos


if __name__ == "__main__":
    try:
        extractor = OpenWeatherExtractor(total_ciudades=100)
        datos = extractor.ejecutar_extraccion()

        os.makedirs("data", exist_ok=True)

        with open("data/clima_raw.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

        df = pd.DataFrame(datos)
        df.to_csv("data/clima.csv", index=False)

        print("\n" + "="*60)
        print("RESUMEN")
        print("="*60)
        print(df.head(10).to_string(index=False))
        print("="*60)

    except Exception as e:
        logger.error(f"❌ Error general: {str(e)}")