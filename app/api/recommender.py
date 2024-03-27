from fastapi import APIRouter, Depends, HTTPException
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from typing import List

router = APIRouter()

es = Elasticsearch("http://localhost:9200")
index_name = "recommendations"
model = SentenceTransformer("quora-distilbert-multilingual")


@router.get("/user_recommendation")
async def get_recommendations(user_tags: str):
    try:
        user_tags = user_tags.split(",")

        query = {
            "query": {
                "bool": {"should": [{"match": {"text": tag}} for tag in user_tags]}
            }
        }

        search_results = es.search(index=index_name, body=query)
        hits = search_results["hits"]["hits"]
        values = [{"id": hit["_id"], **hit["_source"]} for hit in hits]

        return {"data": values}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_elasticsearch_data")
async def get_elasticsearch_data():
    print("get_elasticsearch_data")
    try:
        # Execute a search query to retrieve all documents from the Elasticsearch index
        search_results = es.search(index=index_name, body={"query": {"match_all": {}}})

        # Extract the hits (documents) from the search results
        hits = search_results["hits"]["hits"]

        # Extract values from hits
        values = [{"id": hit["_id"], **hit["_source"]} for hit in hits]

        return {"data": values}
    except Exception as e:
        # Handle exceptions
        raise HTTPException(status_code=500, detail=str(e))
