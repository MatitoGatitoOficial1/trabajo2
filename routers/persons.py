from fastapi import APIRouter

# Crear el objeto router de FastAPI
router = APIRouter()

# Definir una ruta de ejemplo para 'persons'
@router.get("/persons")
async def get_persons():
    return {"message": "Información sobre las personas"}
