# 📘 Documento del Proyecto

## 📝 Descripción

## 🎯 Objetivos

## 🛠️ Tecnologías / Herramientas# 📘 Documento del Proyecto

## 📝 Descripción

Este proyecto desarrolla un pipeline ETL (Extract, Transform, Load) para la recolección, procesamiento y análisis de datos climáticos utilizando la API de OpenWeather.

El sistema extrae información meteorológica en tiempo real a partir de coordenadas geográficas dentro de Estados Unidos, procesa los datos relevantes y los almacena en formatos estructurados (JSON, CSV y PostgreSQL).

Como etapa final, se realizará un análisis estadístico para estudiar la relación entre:

- 🌡️ Temperatura real
- 🥵 Sensación térmica
- 🌬️ Velocidad del viento

El objetivo es identificar patrones y posibles correlaciones que expliquen cómo la velocidad del viento influye en la percepción térmica en distintas ciudades de Estados Unidos.

---

## 🎯 Objetivos

### 🎯 Objetivo General

Desarrollar un sistema automatizado de extracción y análisis de datos climáticos para evaluar la relación entre temperatura, sensación térmica y velocidad del viento en ciudades de Estados Unidos.

### 🎯 Objetivos Específicos

- Implementar un extractor de datos desde la API de OpenWeather.
- Diseñar un proceso de limpieza y transformación de datos.
- Almacenar la información en archivos estructurados y base de datos PostgreSQL.
- Automatizar el entorno mediante Docker.
- Realizar análisis exploratorio de datos (EDA).
- Evaluar correlaciones estadísticas entre las variables.
- Generar visualizaciones para la interpretación de resultados.

---

## 🛠️ Tecnologías / Herramientas

- 💻 VS Code  
- 🐍 Python  
- 🐳 Docker  
- 🐧 WSL  
- 🗄️ PostgreSQL  
- 📊 Jupyter Notebook  
- 🌐 API OpenWeather  
- 📦 Pandas  
- 📈 Matplotlib / Seaborn  

---

## 🗂️ Estructura del Proyecto
```text
Grupo1_Vera_Ferro/
│
├── 📂 data/                     
│   ├── 📄 clima_analysis.png
│   ├── 📄 clima_raw.json            
│   ├── 📄 clima.csv
│
├── 📂 logs/
│   └── 📄 etl.log
│
├── 📂 scripts/
│   ├── 📄 extractor.py               
│   └── 📄 visualizador.py
│
├── 📂 venv/                    
│   ├── 📂 bin 
│   ├── 📂 include
│   ├── 📂 lib
│   ├── 📂 lib64
│   ├── 📂 share
│   └── 📄 pyvenv.cfg
│
├── 📄 .env                  
│
├── 📄 .gitignore
│
├── 📄 README.md
│
└── 📄 requirements.txt

## 👥 Actores

| 👤 Nombre                   | 🎓 Programa      |
| --------------------------- | ---------------- |
| Jose Miguel Vera Garzon     | 💻 Ing. Sistemas |
| Maria Juliana Ferro Bonilla | 💻 Ing. Sistemas |
