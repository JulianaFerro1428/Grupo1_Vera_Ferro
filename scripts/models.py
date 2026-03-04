#!/usr/bin/env python3
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import relationship
from scripts.database import Base


# =====================================================
# TABLA 1: CIUDADES
# =====================================================
class Ciudad(Base):
    __tablename__ = "ciudades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    pais = Column(String(10), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    activa = Column(Boolean, default=True)

    # Relación con registros de clima
    registros_clima = relationship(
        "RegistroClima",
        back_populates="ciudad",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Ciudad(nombre={self.nombre}, pais={self.pais})>"


# =====================================================
# TABLA 2: REGISTROS DE CLIMA
# =====================================================
class RegistroClima(Base):
    __tablename__ = "registros_clima"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ciudad_id = Column(Integer, ForeignKey('ciudades.id'), nullable=False, index=True)

    temperatura = Column(Float, nullable=False)
    sensacion_termica = Column(Float)
    humedad = Column(Float, nullable=False)
    presion = Column(Float)  # 👈 agregado porque tu ETL lo trae
    velocidad_viento = Column(Float, nullable=False)
    descripcion = Column(String(255), nullable=False)

    fecha_extraccion = Column(DateTime, default=datetime.utcnow, index=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relación con ciudad
    ciudad = relationship("Ciudad", back_populates="registros_clima")

    # Índice compuesto (búsquedas rápidas por ciudad + fecha)
    __table_args__ = (
        Index('idx_ciudad_fecha', 'ciudad_id', 'fecha_extraccion'),
    )

    def __repr__(self):
        return f"<RegistroClima(ciudad_id={self.ciudad_id}, temp={self.temperatura})>"


# =====================================================
# TABLA 3: MÉTRICAS ETL
# =====================================================
class MetricasETL(Base):
    __tablename__ = "metricas_etl"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_ejecucion = Column(DateTime, default=datetime.utcnow, index=True)

    registros_extraidos = Column(Integer, nullable=False)
    registros_guardados = Column(Integer, nullable=False)
    registros_fallidos = Column(Integer, default=0)

    tiempo_ejecucion_segundos = Column(Float, nullable=False)

    estado = Column(String(50), nullable=False)  # SUCCESS, PARTIAL, FAILED
    mensaje = Column(String(500))

    def __repr__(self):
        return f"<MetricasETL(estado={self.estado}, registros={self.registros_guardados})>"