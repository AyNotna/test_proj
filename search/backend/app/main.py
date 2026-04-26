from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routers import queries

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Search Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(queries.router)


@app.on_event("startup")
def startup_seed():
    from app.seed import seed
    seed()