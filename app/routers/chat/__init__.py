"""Chat router package."""
from fastapi import APIRouter

from app.routers.chat import endpoints

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

router.include_router(endpoints.router)