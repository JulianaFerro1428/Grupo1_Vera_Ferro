#!/usr/bin/env python3

import os
import json
import random
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import requests
import pandas as pd
from dotenv import load_dotenv


# ======================================
# CONFIGURACIÓN INICIAL
# ======================================

load_dotenv()

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


# ======================================
# CLASE EXTRACTOR
# ======================================

class OpenWeatherExtractor:

    def __init__(self, total_ciudades=100):
        self.api_key = os.getenv("API_KEY")
        self.base_url = os.getenv("OPENWEATHER_URL")
        self.total_ciudades = total_ciudades

        if not self.api_key:
            raise ValueError("API_KEY no configurada en .env")

        if not self.base_url:
            raise ValueError("OPENWEATHER_URL no configurada en .env")

    # ----------------------------------
    # Generar coordenadas en USA
    # ----------------------------------

    def generar_coordenadas_us(self):
        lat = random.uniform(30, 45)
        lon = random.uniform(-120, -70)
        return lat, lon

    # ----------------------------------
    # Llamada a la API
    # ----------------------------------

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
            logger.error(f"Error en coordenadas {lat},{lon}: {e}")
            return None

    # ----------------------------------
    # Procesar respuesta
    # ----------------------------------

    def procesar_respuesta(self, data):

        try:

            ciudad = data.get("name")
            pais = data.get("sys", {}).get("country")

            if not ciudad or pais != "US":
                return None

            return {
                "ciudad": ciudad,
                "pais": pais,
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
            logger.error(f"Error procesando datos: {e}")
            return None

    # ----------------------------------
    # Extracción paralela
    # ----------------------------------

    def ejecutar_extraccion(self):

        ciudades_unicas = set()
        datos = []

        logger.info(f"Buscando {self.total_ciudades} ciudades de EE.UU...")

        with ThreadPoolExecutor(max_workers=20) as executor:

            while len(ciudades_unicas) < self.total_ciudades:

                coordenadas = [
                    self.generar_coordenadas_us()
                    for _ in range(20)
                ]

                resultados = executor.map(
                    lambda c: self.extraer_clima(c[0], c[1]),
                    coordenadas
                )

                for response in resultados:

                    if not response:
                        continue

                    procesado = self.procesar_respuesta(response)

                    if not procesado:
                        continue

                    ciudad = procesado["ciudad"]

                    if ciudad not in ciudades_unicas:

                        ciudades_unicas.add(ciudad)
                        datos.append(procesado)

                        logger.info(
                            f"Ciudad agregada: {ciudad} ({len(ciudades_unicas)}/{self.total_ciudades})"
                        )

                    if len(ciudades_unicas) >= self.total_ciudades:
                        break

        return datos


# ======================================
# MAIN
# ======================================

if __name__ == "__main__":

    try:

        inicio = time.time()

        extractor = OpenWeatherExtractor(total_ciudades=100)
        datos = extractor.ejecutar_extraccion()

        fin = time.time()

        tiempo_total = fin - inicio
        tiempo_promedio = tiempo_total / len(datos)

        # Guardar JSON
        with open("data/clima_raw.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

        # Guardar CSV
        df = pd.DataFrame(datos)
        df.to_csv("data/clima.csv", index=False)

        # Mostrar resumen
        print("\n" + "=" * 60)
        print("RESUMEN DE EXTRACCIÓN")
        print("=" * 60)

        print(df.head(10).to_string(index=False))

        print("=" * 60)
        print(f"\nTotal ciudades extraídas: {len(datos)}")
        print(f"Tiempo total: {tiempo_total:.2f} segundos")
        print(f"Tiempo promedio por ciudad: {tiempo_promedio:.2f} segundos")

    except Exception as e:
        logger.error(f"Error general: {e}")