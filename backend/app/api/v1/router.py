from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    buyers,
    farmers,
    transporters,
    users,
)


api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(farmers.router)
api_router.include_router(buyers.router)
api_router.include_router(transporters.router)
api_router.include_router(admin.router)