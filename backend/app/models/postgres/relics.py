from sqlalchemy import Column, String, Integer, Boolean, JSON
from models.postgres.base import Base

class Relic(Base):
    __tablename__ = "relics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_name = Column(String, unique=True, index=True)
    name = Column(String)
    codex_secret = Column(Boolean, default=False)
    description = Column(String)
    relic_rewards = Column(JSON)
