from fastapi import FastAPI
import pika
from app.api import router as api_router
from fastapi import HTTPException
from elasticsearch import Elasticsearch
from threading import Thread

app = FastAPI(
    title="Recommender Microservice",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api")

es = Elasticsearch("http://localhost:9200")


def on_message_new_offer(channel, method, properties, body):
    """
    Function to run when a message is received from RabbitMQ.
    """
    body = body.decode()

    # Json
    body = eval(body)

    # Insert the offer into the Elasticsearch index
    try:
        es.index(
            index="offers",
            id=body.get("offer_id"),
            body={"tags": body.get("tags")},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def on_message_purchased_offer(channel, method, properties, body):
    """
    Function to run when a message is received from RabbitMQ.
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


def consume_messages():
    """
    Function to consume messages from RabbitMQ.
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="localhost",
            port=5672,
            virtual_host="/",
            credentials=pika.PlainCredentials(username="user", password="user"),
        )
    )

    channel = connection.channel()

    channel.queue_declare(queue="new_offers")
    channel.queue_declare(queue="purchased_offers")

    channel.basic_consume(
        queue="new_offers", on_message_callback=on_message_new_offer, auto_ack=True
    )
    channel.basic_consume(
        queue="purchased_offers",
        on_message_callback=on_message_purchased_offer,
        auto_ack=True,
    )

    channel.start_consuming()


@app.on_event("startup")
async def startup_event():
    """
    Function to run at the startup of the FastAPI application.
    """

    # Start consuming messages in a separate thread
    thread = Thread(target=consume_messages)
    thread.start()
