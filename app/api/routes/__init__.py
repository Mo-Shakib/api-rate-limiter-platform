from app.api.routes.policy import router as policy_router
from app.api.routes.tenants import router as tenants_router
from app.api.routes.keys import router as keys_router
from app.api.routes.protected import router as protected_router
from app.api.routes.usage import router as usage_router

routers = [tenants_router, policy_router, keys_router, protected_router, usage_router]