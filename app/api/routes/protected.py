from fastapi import APIRouter, Depends, Request, Response

from app.api.deps import require_api_key

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/ping")
def ping(request: Request, response: Response, _key=Depends(require_api_key)):
    rl = getattr(request.state, "rate_limit", None) or {}

    # Standard-ish headers
    if rl:
        response.headers["X-RateLimit-Limit"] = str(rl["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rl["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rl["reset"])

    return {"pong": True}