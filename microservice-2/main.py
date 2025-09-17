import os
import uuid
import json
import boto3
from flask import Flask
from pulsar import Client, ConsumerType

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table_name = os.getenv("DYNAMODB_TABLE", "ddd")
table = dynamodb.Table(table_name)

PULSAR_SERVICE_URL = os.getenv("PULSAR_URL", "pulsar://34.228.53.181:6650")
TOPIC_NAME = os.getenv("PULSAR_TOPIC", "persistent://public/default/ddd-items")

client = Client(PULSAR_SERVICE_URL)

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

def listen_and_store():
    consumer = client.subscribe(TOPIC_NAME, subscription_name="microservice-2-sub", consumer_type=ConsumerType.Shared)
    while True:
        msg = consumer.receive()
        try:
            data = json.loads(msg.data())
            item_id = str(uuid.uuid4())
            item = {
                "id": item_id,
                "nombre": data.get("nombre", "unknown"),
                "valor": data.get("valor", 0),
                "status": "procesado por pulsar"
            }
            table.put_item(Item=item)
            consumer.acknowledge(msg)
            print(f"Item stored: {item}")
        except Exception as e:
            consumer.negative_acknowledge(msg)
            print(f"Error processing message: {e}")

if __name__ == "__main__":
    from threading import Thread
    listener_thread = Thread(target=listen_and_store)
    listener_thread.daemon = True
    listener_thread.start()
    app.run(host="0.0.0.0", port=5000)