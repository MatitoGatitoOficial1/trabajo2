from fastapi import FastAPI, HTTPException, Query
from databases import Database
import logging, asyncio, concurrent.futures
from typing import List, Dict, Optional

app = FastAPI(
    title="API de Isekai",
    description="Documentación de la API del trabajo isekai (simulado) como parte de la asignatura Computación Paralela y Distribuida de la UTEM semestre de otoño 2025.",
    version="2.0",
)

DATABASE_URL = "postgresql://isekai:Fr9tL28mQxD7vKcp@159.223.200.213:5432/isekaidb"
database = Database(DATABASE_URL, min_size=5, max_size=20)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cpu_pool = concurrent.futures.ProcessPoolExecutor()


async def get_table_columns(table_name: str) -> List[str]:
    rows = await database.fetch_all(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'isekai' AND table_name = :tbl
        """,
        {"tbl": table_name},
    )
    return [r["column_name"] for r in rows]

async def get_person_identifier() -> str:
    cols = await get_table_columns("persons")
    for col in ("id", "pk", "person_id", "person_pk", "pers_id"):
        if col in cols:
            return col
    raise ValueError("No se encontró la columna ID en persons")


async def _simple_list(tbl: str):
    cols = await get_table_columns(tbl)
    if not cols:
        raise HTTPException(404, f"Tabla {tbl} no encontrada")
    fields = ["pk as id", "code", "name"] + (["description"] if "description" in cols else [])
    q = f"SELECT {', '.join(fields)} FROM isekai.{tbl} ORDER BY name"
    return await database.fetch_all(q)

@app.get("/strata", tags=["Información base"],
         summary="Lista de estratos sociales",
         description="Devuelve todos los estratos con su código, nombre y descripción.")
async def list_strata():
    data = await _simple_list("strata")
    return {"success": True, "count": len(data), "data": data}

@app.get("/species", tags=["Información base"], summary="Lista de especies")
async def list_species():
    data = await _simple_list("species")
    return {"success": True, "count": len(data), "data": data}

@app.get("/genders", tags=["Información base"], summary="Lista de géneros")
async def list_genders():
    data = await _simple_list("genders")
    return {"success": True, "count": len(data), "data": data}


async def calculate_filtered_stats(especie_code: Optional[str],
                                   estrato_code: Optional[int],
                                   genero_code: Optional[str]) -> Dict[str, int | float]:
    id_col = await get_person_identifier()
    base = f"""
    SELECT COUNT(p.{id_col}) AS filtered,
           (SELECT COUNT({id_col}) FROM isekai.persons) AS total
    FROM isekai.persons p
    WHERE 1=1
    """
    p: Dict[str, str | int] = {}
    if especie_code:
        base += " AND EXISTS (SELECT 1 FROM isekai.species s WHERE p.species_fk=s.pk AND s.code=:ec)"
        p["ec"] = especie_code
    if estrato_code is not None:
        base += " AND EXISTS (SELECT 1 FROM isekai.strata st WHERE p.strata_fk=st.pk AND st.code=:sc)"
        p["sc"] = estrato_code
    if genero_code:
        base += " AND EXISTS (SELECT 1 FROM isekai.genders g WHERE p.gender_fk=g.pk AND g.code=:gc)"
        p["gc"] = genero_code
    row = await database.fetch_one(base, p)
    total = row["total"] or 0
    filtrados = row["filtered"] or 0
    pct = round(filtrados / total * 100, 2) if total else 0.0
    return {"filtrados": filtrados, "total": total, "pct": pct}

async def calculate_age_stats(especie_code: Optional[str],
                              estrato_code: Optional[int],
                              genero_code: Optional[str]) -> Dict[str, float]:
    q = """
    SELECT MIN(a)::INT min, MAX(a)::INT max, AVG(a)::NUMERIC(10,2) avg
    FROM (
        SELECT DATE_PART('year', age(current_date, birthdate)) a
        FROM isekai.persons p
        WHERE birthdate IS NOT NULL
    """
    p: Dict[str, str | int] = {}
    if especie_code:
        q += " AND EXISTS (SELECT 1 FROM isekai.species s WHERE p.species_fk=s.pk AND s.code=:ec)"
        p["ec"] = especie_code
    if estrato_code is not None:
        q += " AND EXISTS (SELECT 1 FROM isekai.strata st WHERE p.strata_fk=st.pk AND st.code=:sc)"
        p["sc"] = estrato_code
    if genero_code:
        q += " AND EXISTS (SELECT 1 FROM isekai.genders g WHERE p.gender_fk=g.pk AND g.code=:gc)"
        p["gc"] = genero_code
    q += ") t"
    row = await database.fetch_one(q, p)
    return {
        "edad_min": row["min"] or 0,
        "edad_max": row["max"] or 0,
        "edad_avg": float(row["avg"] or 0),
    }

@app.get(
    "/stats/filter",
    tags=["Estadísticas"],
    summary="Conteo y porcentaje de individuos",
    description="Devuelve cantidad filtrada, total y porcentaje según especie, estrato y género.",
)
async def stats_filter(
    especie: Optional[str] = Query(
        None,
        description="Código de especie (p. ej. HU = Humana, EL = Élfica).",
        example="HU",
    ),
    estrato: Optional[int] = Query(
        None,
        ge=0,
        le=9,
        description="Código numérico de estrato social (0 = Nobleza Suprema … 9 = Desposeídos).",
        example=3,
    ),
    genero: Optional[str] = Query(
        None,
        description="Código de género (M = Masculino, F = Femenino, O = Otro).",
        example="F",
    ),
):
    if especie is None and estrato is None and genero is None:
        raise HTTPException(400, "Debe proporcionar al menos un filtro")
    e = especie.upper() if especie else None
    g = genero.upper() if genero else None
    data = await calculate_filtered_stats(e, estrato, g)
    return {"success": True, "filters": {"e": e, "s": estrato, "g": g}, "results": data}

@app.get(
    "/stats/age",
    tags=["Estadísticas"],
    summary="Estadísticas de edad (mín, máx, promedio)",
    description="Calcula edad mínima, máxima y promedio (años) para los individuos que cumplan los filtros.",
)
async def stats_age(
    especie: Optional[str] = Query(
        None,
        description="Código de especie (p. ej. HU, EL, EN…).",
        example="EL",
    ),
    estrato: Optional[int] = Query(
        None,
        ge=0,
        le=9,
        description="Código numérico de estrato social (0‑9).",
        example=1,
    ),
    genero: Optional[str] = Query(
        None,
        description="Código de género (M, F, O).",
        example="M",
    ),
):
    if especie is None and estrato is None and genero is None:
        raise HTTPException(400, "Debe proporcionar al menos un filtro")
    e = especie.upper() if especie else None
    g = genero.upper() if genero else None
    data = await calculate_age_stats(e, estrato, g)
    return {"success": True, "filters": {"e": e, "s": estrato, "g": g}, "results": data}


def heavy_computation(_: int) -> float:
    steps = 10_000_000
    acc = 0.0
    for i in range(steps):
        x = (i + 0.5) / steps
        acc += 4.0 / (1.0 + x * x)
    return acc / steps

@app.get("/cpu/heavy", include_in_schema=False)
async def cpu_heavy(iteraciones: int = Query(1, ge=1, le=5)):
    loop = asyncio.get_running_loop()
    resultados = await asyncio.gather(*[
        loop.run_in_executor(cpu_pool, heavy_computation, i)
        for i in range(iteraciones)
    ])
    return {"iteraciones": iteraciones, "resultados": resultados}


@app.on_event("startup")
async def startup():
    await database.connect()
    logger.info("Conexión a DB establecida")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    cpu_pool.shutdown()
    logger.info("DB desconectada y pool CPU cerrado")

@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "API de Isekai – v2.8.0 (paralelismo CPU y async I/O)",
        "docs": "/docs",
        "endpoints": {
            "catálogos": ["/strata", "/species", "/genders"],
            "estadísticas": ["/stats/filter", "/stats/age"]
        }
    }