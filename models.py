from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Species(Base):
    __tablename__ = "species"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class Strata(Base):
    __tablename__ = "strata"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class Gender(Base):
    __tablename__ = "genders"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    species_id = Column(Integer, ForeignKey("species.id"))
    strata_id = Column(Integer, ForeignKey("strata.id"))
    gender_id = Column(Integer, ForeignKey("genders.id"))
