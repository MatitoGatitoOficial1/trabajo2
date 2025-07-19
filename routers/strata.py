from fastapi import APIRouter

# Crear el objeto router de FastAPI
router = APIRouter()

# Definir una ruta de ejemplo para 'strata'
@router.get("/strata")
async def get_strata():
    return {"message": "Información sobre los estratos sociales"}
