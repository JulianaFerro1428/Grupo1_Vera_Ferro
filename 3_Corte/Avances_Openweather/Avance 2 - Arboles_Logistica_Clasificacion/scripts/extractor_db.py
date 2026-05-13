#!/usr/bin/env python3
import os
import time
import logging
import pandas as pd
from datetime import datetime

from sqlalchemy.dialects.postgresql import insert

from scripts.database import SessionLocal, create_all_tables
from scripts.models import Ciudad, RegistroClima, MetricasETL

# ==============================
# CONFIGURACIÓN
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


class OpenWeatherETL:

    def __init__(self):
        create_all_tables()
        self.db = SessionLocal()

        self.tiempo_inicio = time.time()
        self.registros_extraidos = 0
        self.registros_guardados = 0
        self.registros_fallidos = 0

    # ==============================
    # EJECUTAR ETL
    # ==============================
    def ejecutar(self):
        try:
            logger.info("🚀 Iniciando carga a BD desde CSV...")

            path = "data/clima_transformado.csv"

            if not os.path.exists(path):
                logger.error("❌ No existe clima_transformado.csv")
                return False

            df = pd.read_csv(path)
            self.registros_extraidos = len(df)

            logger.info(f"📊 Registros a insertar: {self.registros_extraidos}")

            # ==============================
            # 1. CIUDADES (UPSERT REAL - SIN DUPLICADOS)
            # ==============================
            ciudades_unicas = df["ciudad"].dropna().unique()

            ciudades_data = [
                {
                    "nombre": str(nombre),
                    "pais": "US",
                    "activa": True
                }
                for nombre in ciudades_unicas
            ]

            if ciudades_data:
                stmt = insert(Ciudad.__table__).values(ciudades_data)

                # ✅ CORREGIDO AQUÍ
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=["nombre"]
                )

                self.db.execute(stmt)
                self.db.commit()

            # ==============================
            # MAPEO DE CIUDADES
            # ==============================
            ciudades_db = self.db.query(Ciudad).all()
            ciudad_map = {c.nombre: c for c in ciudades_db}

            logger.info(f"🏙️ Ciudades en BD: {len(ciudad_map)}")

            # ==============================
            # 2. REGISTROS CLIMA
            # ==============================
            registros = []

            for _, row in df.iterrows():
                try:
                    ciudad = ciudad_map.get(str(row["ciudad"]))

                    if not ciudad:
                        self.registros_fallidos += 1
                        continue

                    registros.append(RegistroClima(
                        ciudad_id=ciudad.id,
                        temperatura=row.get("temperatura", 0),
                        sensacion_termica=row.get("sensacion_termica", 0),
                        humedad=row.get("humedad", 0),
                        presion=row.get("presion", 0),
                        velocidad_viento=row.get("velocidad_viento", 0),
                        descripcion=str(row.get("descripcion", "N/A")),
                        fecha_extraccion=datetime.now()
                    ))

                except Exception:
                    self.registros_fallidos += 1

            # ==============================
            # BULK INSERT CLIMA
            # ==============================
            if registros:
                self.db.bulk_save_objects(registros)
                self.db.commit()

            self.registros_guardados = len(registros)

            logger.info(f"✅ Insertados: {self.registros_guardados}")

            # ==============================
            # MÉTRICAS ETL
            # ==============================
            tiempo_total = time.time() - self.tiempo_inicio

            metricas = MetricasETL(
                registros_extraidos=self.registros_extraidos,
                registros_guardados=self.registros_guardados,
                registros_fallidos=self.registros_fallidos,
                tiempo_ejecucion_segundos=tiempo_total,
                estado="SUCCESS"
            )

            self.db.add(metricas)
            self.db.commit()

            logger.info("📈 Métricas guardadas")
            logger.info("🎉 ETL COMPLETADO")

            return True

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False

        finally:
            self.db.close()


# ==============================
if __name__ == "__main__":
    etl = OpenWeatherETL()
    exito = etl.ejecutar()
    exit(0 if exito else 1)