from sqlalchemy.future import select
from models import Species, Strata, Gender, Person
from database import SessionLocal

# Funciones CRUD para Species
async def get_species(db):
    result = await db.execute(select(Species))
    return result.scalars().all()

# Funciones CRUD para Strata
async def get_strata(db):
    result = await db.execute(select(Strata))
    return result.scalars().all()

# Funciones CRUD para Gender
async def get_genders(db):
    result = await db.execute(select(Gender))
    return result.scalars().all()

# Funciones CRUD para Person
async def get_persons(db):
    result = await db.execute(select(Person))
    return result.scalars().all()
