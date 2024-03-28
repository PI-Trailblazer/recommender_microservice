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


def on_message(channel, method, properties, body):
    """
    Function to run when a message is received from RabbitMQ.
    """
    body = body.decode()

    # Json
    body = eval(body)

    print(f"Offer id: {body.get('offer_id')}")


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
    channel.basic_consume(
        queue="new_offers", on_message_callback=on_message, auto_ack=True
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
