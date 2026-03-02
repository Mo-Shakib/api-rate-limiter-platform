from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth_rate_limit import enforce_api_key_and_rate_limit


def require_api_key(request: Request, db: Session = Depends(get_db)):
    return enforce_api_key_and_rate_limit(request, db)