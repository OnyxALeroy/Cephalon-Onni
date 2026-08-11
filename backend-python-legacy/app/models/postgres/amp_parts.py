from sqlalchemy import Column, String, Integer, Boolean
from models.postgres.base import Base


class AmpPart(Base):
    __tablename__ = "amp_parts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_name = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(String)
    codex_secret = Column(Boolean, default=False)
    component_type = Column(String)
