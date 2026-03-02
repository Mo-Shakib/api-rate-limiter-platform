from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.api.routes import routers


app = FastAPI(title=settings.APP_NAME)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


for r in routers:
    app.include_router(r)