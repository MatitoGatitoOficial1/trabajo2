from fastapi import APIRouter

router = APIRouter()

@router.get("/genders")
async def get_genders():
    return {"message": "Información sobre los géneros"}