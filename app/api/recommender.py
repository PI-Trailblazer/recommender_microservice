from fastapi import APIRouter, HTTPException
from elasticsearch import Elasticsearch

router = APIRouter()

es = Elasticsearch("http://localhost:9200")


@router.get("/most_relevant")
async def get_elasticsearch_data(size: int):
    try:
        # Execute a search query to retrieve the most 10 relevant documents
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
