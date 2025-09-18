from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True)
    nombre = Column(String)
    valor = Column(Integer)
    estado = Column(String)