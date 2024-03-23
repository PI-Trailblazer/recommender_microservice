from fastapi import APIRouter

from . import recommender

router = APIRouter()

router.include_router(user.router, prefix="/recommender", tags=["recommender"])
