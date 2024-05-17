from contextlib import asynccontextmanager
from fastapi import FastAPI
import pika

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api import router as api_router
from fastapi import HTTPException
from elasticsearch import Elasticsearch
from threading import Thread
from app.core.config import settings
import loguru

app = FastAPI(
    title="Recommender Microservice",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

es = Elasticsearch("http://elasticsearch:9200")


def on_message_new_offer(channel, method, properties, body):
    """
    Function to add a new offer to the Elasticsearch index.
    """
    body = body.decode()

    # Json
    body = eval(body)

    # Insert the offer into the Elasticsearch index
    try:
        es.index(
            index="offers",
            id=body.get("offer_id"),
            body={"tags": body.get("tags"), "relevance_score": 0},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def on_message_purchased_offer(channel, method, properties, body):
    """
    Function to update the relevance_score of an offer in the Elasticsearch index.
    """
    body = body.decode()

    # Json
    body = eval(body)

    # Add 1 to the relavence_score of the offer in the Elasticsearch index
    try:
        offer = es.get(index="offers", id=body.get("offer_id"))
        relevance_score = offer.get("_source").get("relevance_score", 0) + 1
        es.update(
            index="offers",
            id=body.get("offer_id"),
            body={"doc": {"relevance_score": relevance_score}},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def on_message_delete_offer(channel, method, properties, body):
    """
    Function to delete an offer from the Elasticsearch index.
    """
    body = body.decode()

    # Json
    body = eval(body)

    # Delete the offer from the Elasticsearch index
    try:
        es.delete(index="offers", id=body.get("offer_id"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def consume_messages():
    """
    Function to consume messages from RabbitMQ.
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rabbitmq",
            port=5672,
            virtual_host="/",
            credentials=pika.PlainCredentials(username="user", password="user"),
        )
    )

    channel = connection.channel()

    channel.queue_declare(queue="new_offers")
    channel.queue_declare(queue="purchased_offers")
    channel.queue_declare(queue="delete_offer")

    channel.basic_consume(
        queue="new_offers", on_message_callback=on_message_new_offer, auto_ack=True
    )
    channel.basic_consume(
        queue="purchased_offers",
        on_message_callback=on_message_purchased_offer,
        auto_ack=True,
    )
    channel.basic_consume(
        queue="delete_offer",
        on_message_callback=on_message_delete_offer,
        auto_ack=True,
    )

    channel.start_consuming()


async def startup_event():
    """
    Function to run at the startup of the FastAPI application.
    """
    # create index on es
    loguru.logger.info("Creating index on Elasticsearch")
    if not es.indices.exists(index="offers"):
        # Create the index
        es.indices.create(index="offers")
    # Start consuming messages in a separate thread
    thread = Thread(target=consume_messages)
    thread.start()


app.add_event_handler("startup", startup_event)
