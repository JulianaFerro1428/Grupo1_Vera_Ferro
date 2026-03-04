from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from scripts.database import Base
from datetime import datetime


class Ciudad(Base):
    __tablename__ = "ciudades"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    pais = Column(String)
    latitud = Column(Float)
    longitud = Column(Float)
    activa = Column(Boolean, default=True)

    registros = relationship("RegistroClima", back_populates="ciudad")


class RegistroClima(Base):
    __tablename__ = "registros_clima"

    id = Column(Integer, primary_key=True, index=True)
    ciudad_id = Column(Integer, ForeignKey("ciudades.id"))
    temperatura = Column(Float)
    sensacion_termica = Column(Float)
    humedad = Column(Integer)
    presion = Column(Integer)
    velocidad_viento = Column(Float)
    descripcion = Column(String)
    fecha_extraccion = Column(DateTime, default=datetime.utcnow)

    ciudad = relationship("Ciudad", back_populates="registros")


class MetricasETL(Base):
    __tablename__ = "metricas_etl"

    id = Column(Integer, primary_key=True)
    registros_extraidos = Column(Integer)
    registros_guardados = Column(Integer)
    registros_fallidos = Column(Integer)
    tiempo_ejecucion_segundos = Column(Float)
    estado = Column(String)
    fecha_ejecucion = Column(DateTime, default=datetime.utcnow)