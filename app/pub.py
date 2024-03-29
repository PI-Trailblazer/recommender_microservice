import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        port=5672,
        virtual_host="/",
        credentials=pika.PlainCredentials(username="user", password="user"),
    )
)

channel = connection.channel()

# publish a message to the new_offers queue with a json payload with offer and a list with tags
channel.basic_publish(
    exchange="",
    routing_key="new_offers",
    body='{"offer_id": "15", "tags": ["clothes", "shoes"]}',
)

# publish a message to the purchased_offers queue with a json payload with offer_id
channel.basic_publish(
    exchange="",
    routing_key="purchased_offers",
    body='{"offer_id": "15"}',
)
