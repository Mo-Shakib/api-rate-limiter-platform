from app.api.routes.policy import router as policy_router
from app.api.routes.tenants import router as tenants_router

routers = [tenants_router, policy_router]