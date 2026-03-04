#!/usr/bin/env python3
import os
import requests
import random
import time
from datetime import datetime
from dotenv import load_dotenv
import logging
from sqlalchemy.exc import IntegrityError

from scripts.database import SessionLocal
from scripts.models import Ciudad, RegistroClima, MetricasETL

# ==============================
# Configuración inicial
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


class OpenWeatherETL:

    def __init__(self, total_ciudades=5):
        self.api_key = os.getenv("API_KEY")
        self.base_url = os.getenv("OPENWEATHER_URL")
        self.total_ciudades = total_ciudades

        self.db = SessionLocal()

        self.tiempo_inicio = time.time()
        self.registros_extraidos = 0
        self.registros_guardados = 0
        self.registros_fallidos = 0

        if not self.api_key:
            raise ValueError("API_KEY no configurada en .env")

        if not self.base_url:
            raise ValueError("OPENWEATHER_URL no configurada en .env")

    # ==============================
    # Generar coordenadas USA
    # ==============================
    def generar_coordenadas_us(self):
        lat = random.uniform(24.5, 49.5)
        lon = random.uniform(-125, -66)
        return lat, lon

    # ==============================
    # Extraer clima
    # ==============================
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

            self.registros_extraidos += 1
            return response.json()

        except Exception as e:
            logger.error(f"❌ Error en API: {str(e)}")
            self.registros_fallidos += 1
            return None

    # ==============================
    # Procesar respuesta
    # ==============================
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
            }

        except Exception as e:
            logger.error(f"Error procesando datos: {str(e)}")
            return None

    # ==============================
    # Guardar en BD
    # ==============================
    def guardar_en_bd(self, datos):
        try:
            ciudad = self.db.query(Ciudad).filter_by(
                nombre=datos["ciudad"]
            ).first()

            if not ciudad:
                ciudad = Ciudad(
                    nombre=datos["ciudad"],
                    pais=datos["pais"],
                    latitud=datos["latitud"],
                    longitud=datos["longitud"]
                )
                self.db.add(ciudad)
                self.db.flush()

            registro = RegistroClima(
                ciudad_id=ciudad.id,
                temperatura=datos["temperatura"],
                sensacion_termica=datos["sensacion_termica"],
                humedad=datos["humedad"],
                presion=datos["presion"],
                velocidad_viento=datos["velocidad_viento"],
                descripcion=datos["descripcion"],
                fecha_extraccion=datetime.utcnow()
            )

            self.db.add(registro)
            self.db.commit()
            self.registros_guardados += 1

            logger.info(f"📊 Registro guardado: {datos['ciudad']}")

        except IntegrityError:
            self.db.rollback()
            self.registros_fallidos += 1
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error guardando en BD: {str(e)}")
            self.registros_fallidos += 1

    # ==============================
    # Guardar métricas
    # ==============================
    def guardar_metricas(self, estado):
        try:
            tiempo_total = time.time() - self.tiempo_inicio

            metricas = MetricasETL(
                registros_extraidos=self.registros_extraidos,
                registros_guardados=self.registros_guardados,
                registros_fallidos=self.registros_fallidos,
                tiempo_ejecucion_segundos=tiempo_total,
                estado=estado,
                mensaje=f"Extraídos: {self.registros_extraidos}, Guardados: {self.registros_guardados}, Fallidos: {self.registros_fallidos}"
            )

            self.db.add(metricas)
            self.db.commit()

        except Exception as e:
            logger.error(f"Error guardando métricas: {str(e)}")

    # ==============================
    # Ejecutar ETL completo
    # ==============================
    def ejecutar(self):
        try:
            ciudades_unicas = set()

            logger.info("🚀 Iniciando ETL OpenWeather...")

            while len(ciudades_unicas) < self.total_ciudades:

                lat, lon = self.generar_coordenadas_us()
                response = self.extraer_clima(lat, lon)

                if response:
                    datos = self.procesar_respuesta(response)

                    if datos and datos["ciudad"] not in ciudades_unicas:
                        ciudades_unicas.add(datos["ciudad"])
                        self.guardar_en_bd(datos)

                time.sleep(1)

            estado = "SUCCESS" if self.registros_fallidos == 0 else "PARTIAL"
            self.guardar_metricas(estado)

            return estado == "SUCCESS"

        except Exception as e:
            logger.error(f"Error general ETL: {str(e)}")
            self.guardar_metricas("FAILED")
            return False

        finally:
            self.db.close()


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    etl = OpenWeatherETL(total_ciudades=5)
    exito = etl.ejecutar()
    exit(0 if exito else 1)