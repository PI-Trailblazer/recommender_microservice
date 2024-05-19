from typing import List
from fastapi import APIRouter, HTTPException, Query, Security
from app.api import auth_deps
from elasticsearch import Elasticsearch

router = APIRouter()

es = Elasticsearch("http://elasticsearch:9200")


@router.get("/most_relevant")
async def get_elasticsearch_data(size: int):
    try:
        # Execute a search query to retrieve the most 10 relevant documents
        if es.count(index="offers")["count"] == 0:
            return {"data": []}
        search_results = es.search(
            index="offers",
            body={
                "size": size,
                "query": {
                    "function_score": {
                        "query": {"match_all": {}},
                        "functions": [
                            {
                                "field_value_factor": {
                                    "field": "relevance_score",
                                    "factor": 1,
                                }
                            }
                        ],
                    }
                },
            },
        )
        # Extract the hits (documents) from the search results
        hits = search_results["hits"]["hits"]
        # Extract only the ids from hits
        values = [hit["_id"] for hit in hits]
        return {"data": values}
    except Exception as e:
        # Handle exceptions
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user_recommendation")
async def get_recommendations(
    size: int, payload=Security(auth_deps.verify_token, scopes=[])
):
    user_tags = payload["tags"]
    try:
        if es.count(index="offers")["count"] == 0:
            return {"data": []}
        search_results = es.search(
            index="offers",
            body={
                "size": size,
                "query": {
                    "function_score": {
                        "query": {
                            "bool": {
                                "should": [
                                    {"match": {"tags": tag}} for tag in user_tags
                                ]
                            }
                        },
                        "functions": [
                            {
                                "field_value_factor": {
                                    "field": "relevance_score",
                                    "factor": 1,
                                }
                            }
                        ],
                    }
                },
            },
        )

        # Extract the hits (documents) from the search results
        hits = search_results["hits"]["hits"]

        # Extract only the ids from hits
        values = [hit["_id"] for hit in hits]

        return {"data": values}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/offer_recommendation")
async def get_recommendations(size: int, offer_tags: List[str]):

    try:
        if es.count(index="offers")["count"] == 0:
            return {"data": []}

        search_results = es.search(
            index="offers",
            body={
                "size": size,
                "query": {
                    "function_score": {
                        "query": {
                            "bool": {
                                "should": [
                                    {"match": {"tags": tag}} for tag in offer_tags
                                ]
                            }
                        },
                        "functions": [
                            {
                                "field_value_factor": {
                                    "field": "relevance_score",
                                    "factor": 1,
                                }
                            }
                        ],
                    }
                },
            },
        )

        # Extract the hits (documents) from the search results
        hits = search_results["hits"]["hits"]

        # Extract only the ids from hits
        values = [hit["_id"] for hit in hits]

        return {"data": values}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
