from sqlalchemy import Column, String, Integer, Boolean, JSON
from models.postgres.base import Base


class Companion(Base):
    __tablename__ = "companions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_name = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(String)
    health = Column(Integer)
    shield = Column(Integer)
    armor = Column(Integer)
    stamina = Column(Integer)
    power = Column(Integer)
    codex_secret = Column(Boolean, default=False)
    exclude_from_codex = Column(Boolean, default=False)
    product_category = Column(String)
