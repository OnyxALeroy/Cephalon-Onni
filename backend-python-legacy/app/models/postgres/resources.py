from sqlalchemy import Column, String, Integer, Boolean
from models.postgres.base import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_name = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(String)
    codex_secret = Column(Boolean, default=False)
    parent_name = Column(String)
    exclude_from_codex = Column(Boolean, default=False)
    show_in_inventory = Column(Boolean, default=False)
    prime_selling_price = Column(Integer)
