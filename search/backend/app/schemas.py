from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class QueryBase(BaseModel):
    name: str
    status: str
    deadline: datetime


class QueryCreate(QueryBase):
    pass


class QueryUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None


class QueryResponse(QueryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    owner: str
    results_count: int
    is_overdue: bool = False

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    data: list[QueryResponse]
    total: int
    page: int
    limit: int