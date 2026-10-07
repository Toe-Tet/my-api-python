from fastapi import APIRouter

from app.modules.auth.auth_router import auth_router
from app.modules.tenancy.farmers.farmer_router import farmer_router
from app.modules.users.user_router import user_router

# Prepare router
router = APIRouter(prefix="/api")
v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")

# V1 Router
v1_router.include_router(auth_router)
v1_router.include_router(farmer_router)
v1_router.include_router(user_router)

# V2 Router
v2_router.include_router(auth_router)
v2_router.include_router(farmer_router)
v2_router.include_router(user_router)

# Assign router
router.include_router(v1_router)
router.include_router(v2_router)
