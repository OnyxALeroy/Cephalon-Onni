from sqlalchemy import Column, String, Integer, Boolean, JSON
from models.postgres.base import Base

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_name = Column(String, unique=True, index=True)
    build_price = Column(Integer)
    build_time = Column(Integer)
    skip_build_time_price = Column(Integer)
    consume_on_use = Column(Boolean)
    num = Column(Integer)
    codex_secret = Column(Boolean, default=False)
    result_type = Column(String)
    ingredients = Column(JSON)
