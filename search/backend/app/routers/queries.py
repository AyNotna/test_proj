from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random

from app.database import get_db
from app.models import SearchQuery
from app.schemas import QueryCreate, QueryUpdate
from faker import Faker

router = APIRouter(prefix="/api/queries", tags=["queries"])

ALLOWED_SORT_FIELDS = {
    "name": SearchQuery.name,
    "created_at": SearchQuery.created_at,
    "updated_at": SearchQuery.updated_at,
    "status": SearchQuery.status,
    "owner": SearchQuery.owner,
    "deadline": SearchQuery.deadline,
    "results_count": SearchQuery.results_count,
}


@router.get("/")
def get_queries(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
):
    sort_field = ALLOWED_SORT_FIELDS.get(sort, SearchQuery.created_at)
    if order == "asc":
        sort_field = sort_field.asc()
    else:
        sort_field = sort_field.desc()

    total = db.query(SearchQuery).count()
    queries = (
        db.query(SearchQuery)
        .order_by(sort_field)
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    now = datetime.utcnow()
    data = []
    for q in queries:
        data.append({
            "id": q.id,
            "name": q.name,
            "created_at": q.created_at.isoformat(),
            "updated_at": q.updated_at.isoformat(),
            "status": q.status,
            "owner": q.owner,
            "deadline": q.deadline.isoformat(),
            "results_count": q.results_count,
            "is_overdue": q.deadline < now and q.status == "active",
        })

    return {"data": data, "total": total, "page": page, "limit": limit}


@router.post("/")
def create_query(query: QueryCreate, db: Session = Depends(get_db)):
    fake = Faker('ru_RU')
    db_query = SearchQuery(
        name=query.name,
        status=query.status,
        deadline=query.deadline,
        owner=fake.email(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        results_count=random.randint(0, 10000),
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query


@router.put("/{query_id}")
def update_query(query_id: int, query: QueryUpdate, db: Session = Depends(get_db)):
    db_query = db.query(SearchQuery).filter(SearchQuery.id == query_id).first()
    if not db_query:
        raise HTTPException(status_code=404, detail="Не найдено")
    if query.name is not None:
        db_query.name = query.name
    if query.status is not None:
        db_query.status = query.status
    if query.deadline is not None:
        db_query.deadline = query.deadline
    db_query.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_query)
    return db_query


@router.delete("/{query_id}")
def delete_query(query_id: int, db: Session = Depends(get_db)):
    db_query = db.query(SearchQuery).filter(SearchQuery.id == query_id).first()
    if not db_query:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(db_query)
    db.commit()
    return {"ok": True}


@router.post("/delete-many")
def delete_many(ids: list[int], db: Session = Depends(get_db)):
    result = db.query(SearchQuery).filter(SearchQuery.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return {"ok": True, "deleted": result}