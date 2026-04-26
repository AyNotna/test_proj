from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime
import datetime


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    status = Column(String, default="active")
    owner = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=False)
    results_count = Column(Integer, default=0)