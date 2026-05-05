#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# ==============================
# CONFIG DINÁMICA (Streamlit o local)
# ==============================
def _get_db_config():
    # Intento 1: Streamlit Cloud
    try:
        import streamlit as st
        host = st.secrets.get("DB_HOST", "")
        if host and host != "localhost":
            return {
                "host":     host,
                "port":     st.secrets.get("DB_PORT", "5432"),
                "user":     st.secrets.get("DB_USER", "postgres"),
                "password": st.secrets.get("DB_PASSWORD", ""),
                "dbname":   st.secrets.get("DB_NAME", "postgres"),
            }
    except Exception:
        pass

    # Intento 2: LOCAL (.env o valores por defecto)
    return {
        "host":     os.getenv("DB_HOST", "aws-1-us-east-1.pooler.supabase.com"),
        "port":     os.getenv("DB_PORT", "6543"),
        "user":     os.getenv("DB_USER", "postgres.ddnwsxvyfhnwygiddlar"),
        "password": os.getenv("DB_PASSWORD", "JulianaFerro1428"),
        "dbname":   os.getenv("DB_NAME", "postgres"),
    }


# ==============================
# CREAR CONEXIÓN
# ==============================
config = _get_db_config()

DATABASE_URL = (
    f"postgresql://{config['user']}:{config['password']}"
    f"@{config['host']}:{config['port']}/{config['dbname']}"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True  
    )

Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

metadata = MetaData()


# ==============================
# FUNCIONES
# ==============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("✅ Conexión a PostgreSQL exitosa")
            return True
    except Exception as e:
        logger.error(f"❌ Error conectando a PostgreSQL: {str(e)}")
        return False


def create_all_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas exitosamente")
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {str(e)}")