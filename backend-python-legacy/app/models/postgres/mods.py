from sqlalchemy import Column, String, Integer, Boolean, JSON
from models.postgres.base import Base

class Mod(Base):
    __tablename__ = "mods"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_name = Column(String, unique=True, index=True)
    name = Column(String)
    polarity = Column(String)
    rarity = Column(String)
    type = Column(String)
    subtype = Column(String)
    codex_secret = Column(Boolean, default=False)
    base_drain = Column(Integer)
    fusion_limit = Column(Integer)
    compat_name = Column(String)
    mod_set = Column(String)
    mod_set_values = Column(JSON)
    is_utility = Column(Boolean)
    description = Column(JSON)
    level_stats = Column(JSON)
    upgrade_entries = Column(JSON)
    available_challenges = Column(JSON)
