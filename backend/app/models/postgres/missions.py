from sqlalchemy import Column, String, Integer, JSON
from models.postgres.base import Base

class Mission(Base):
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_name = Column(String, unique=True, index=True)
    mission_name = Column(String)
    system_name = Column(String)
    planet = Column(String)
    type = Column(String)
    node_type = Column(Integer)
    faction_index = Column(Integer)
    mastery_req = Column(Integer)
    min_enemy_level = Column(Integer)
    max_enemy_level = Column(Integer)
    mission_index = Column(Integer)
    system_index = Column(Integer)
    drops = Column(JSON)
