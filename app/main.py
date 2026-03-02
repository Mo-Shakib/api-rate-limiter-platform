from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import routers
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # If rate limit info exists, attach headers even for 429 errors
    headers = {}
    rl = getattr(request.state, "rate_limit", None)
    if rl:
        headers["X-RateLimit-Limit"] = str(rl["limit"])
        headers["X-RateLimit-Remaining"] = str(rl["remaining"])
        headers["X-RateLimit-Reset"] = str(rl["reset"])

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=headers)


for r in routers:
    app.include_router(r)