from fastapi import APIRouter
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from . import recommender

router = APIRouter()

router.include_router(recommender.router, prefix="/recommender", tags=["recommender"])

es = Elasticsearch("http://localhost:9200")
model = SentenceTransformer("quora-distilbert-multilingual")
index_name = "offers"

offers = [
    {"offer_id": 1, "tags": ["tag1", "tag2", "tag3"]},
    {"offer_id": 2, "tags": ["tag4", "tag5", "tag6"]},
    {"offer_id": 3, "tags": ["tag7", "tag8", "tag9"]},
]


def clear_index():
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print("Index deleted.")


def create_index():
    es.indices.create(
        index=index_name,
        body={
            "mappings": {
                "properties": {
                    "text": {"type": "text"},
                }
            }
        },
    )
    print("Index created.")


clear_index()
create_index()

for offer in offers:
    embedding = model.encode(offer["tags"], show_progress_bar=False)
    es.index(
        index=index_name,
        body={"text": offer["tags"]},
    )
