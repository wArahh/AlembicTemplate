from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Credentials(Base):
    __tablename__ = 'credentials'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True, nullable = False)
    password = Column(String, nullable = False)
