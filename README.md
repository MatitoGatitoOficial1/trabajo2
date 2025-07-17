## 🚀 API de Isekai - Compu paralela

API REST para gestión de datos demográficos en un mundo fantástico, implementando paralelismo con FastAPI y PostgreSQL.

## 📌 Características principales
- **Endpoints CRUD** para especies, estratos sociales y géneros.
- **Estadísticas paralelizadas** con `ProcessPoolExecutor`.
- **Documentación automática** (Swagger UI y ReDoc).
- **Conexión asíncrona** a PostgreSQL con `asyncpg`.

## 🔧 Requisitos
- Python 3.8+
- PostgreSQL 16+
- Pip

## 🛠️ Instalación
``` 
# Clonar repositorio
git clone https://github.com/tu-usuario/isekai-api.git
cd isekai-api

# Crear entorno virtual (Linux)
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```
## EJECUCIÓN
# Modo desarrollo (con recarga automática)
uvicorn app.main:app --reload

# Modo producción (con Gunicorn)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

´´´
Endpoints principales
Endpoint	Descripción	Método
/strata	Lista de estratos sociales	GET
/species	Lista de especies	GET
/stats/filter	Estadísticas filtradas	GET
/cpu/heavy	Tareas CPU paralelizadas (oculto)	GET

