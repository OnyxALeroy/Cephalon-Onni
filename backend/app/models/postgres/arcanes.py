from sqlalchemy import Column, String, Integer, Boolean, JSON
from models.postgres.base import Base


class Arcane(Base):
    __tablename__ = "arcanes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_name = Column(String, unique=True, index=True)
    name = Column(String)
    codex_secret = Column(Boolean, default=False)
    rarity = Column(String)
    level_stats = Column(JSON)
