from pydantic import BaseModel

class SpeciesOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class StrataOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class GenderOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class PersonOut(BaseModel):
    id: int
    name: str
    species_id: int
    strata_id: int
    gender_id: int
    class Config:
        orm_mode = True
