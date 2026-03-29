from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ARRAY
from models.postgres.base import Base

class Warframe(Base):
    __tablename__ = "warframes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_name = Column(String, unique=True, index=True)
    name = Column(String)
    parent_name = Column(String)
    description = Column(String)
    health = Column(Integer)
    shield = Column(Integer)
    armor = Column(Integer)
    stamina = Column(Integer)
    power = Column(Integer)
    codex_secret = Column(Boolean, default=False)
    mastery_req = Column(Integer)
    sprint_speed = Column(Float)
    passive_description = Column(String)
    exalted = Column(JSON)
    abilities = Column(JSON)
    product_category = Column(String)
