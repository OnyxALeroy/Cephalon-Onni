from sqlalchemy import Column, String, Float, Integer, UniqueConstraint
from models.postgres.base import Base

class DropSource(Base):
    __tablename__ = "drop_sources"
    __table_args__ = (UniqueConstraint('name', 'source', name='uq_drop_sources_name_source'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    source_type = Column(String)
    source = Column(String)
    chance = Column(Float)
    rotation = Column(String)
