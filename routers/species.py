from fastapi import APIRouter

# Crear el objeto router de FastAPI
router = APIRouter()

# Definir una ruta de ejemplo para 'species'
@router.get("/species")
async def get_species():
    return {"message": "Información sobre las especies"}
