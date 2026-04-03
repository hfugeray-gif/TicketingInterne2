from fastapi import FastAPI

from app.api.routes.comments import router as comments_router
from app.api.routes.health import router as health_router
from app.api.routes.journal import router as journal_router
from app.api.routes.merge import router as merge_router
from app.api.routes.tickets import router as tickets_router
from app.api.routes.config import router as config_router
from app.api.routes.me import router as me_router
from app.db import models
from app.db.base import Base
from app.db.session import engine

app = FastAPI(
    title="Ticketing API",
    version="0.1.0",
)


app.include_router(health_router)
app.include_router(tickets_router)
app.include_router(comments_router)
app.include_router(journal_router)
app.include_router(merge_router)
app.include_router(config_router)
app.include_router(me_router)


@app.get("/")
def root():
    return {"message": "Ticketing API is running"}