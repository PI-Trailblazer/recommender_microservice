from fastapi import APIRouter

from . import recommender

router = APIRouter()

router.include_router(recommender.router, prefix="/recommender", tags=["recommender"])
