from fastapi import APIRouter, HTTPException
from elasticsearch import Elasticsearch

router = APIRouter()

es = Elasticsearch("http://localhost:9200")


@router.get("/user_recommendation")
async def get_recommendations(user_tags: str, size: int):
    try:
        user_tags = user_tags.split(",")

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
