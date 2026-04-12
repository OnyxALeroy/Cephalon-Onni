from sqlalchemy import Column, String, Integer
from models.postgres.base import Base

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_name = Column(String, unique=True, index=True)
    texture_location = Column(String)
