from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Query(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True)
    query_text = Column(String)
    response = Column(String)
    timestamp = Column(DateTime)