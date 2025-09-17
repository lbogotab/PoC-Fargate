from flask import Flask, jsonify

app = Flask(__name__)

import boto3
import uuid
import os
import requests
from flask import request

# Nombre de la tabla DynamoDB, se puede setear por variable de entorno
DYNAMO_TABLE = os.getenv("DYNAMO_TABLE", "ddd")

# Cliente de DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(DYNAMO_TABLE)

@app.route("/save", methods=["POST"])
def save_item():
    data = request.get_json()
    item_id = str(uuid.uuid4())

    item = {
        "id": item_id,
        "nombre": data.get("nombre", "N/A"),
        "valor": data.get("valor", 0)
    }

    try:
        table.put_item(Item=item)
        # Publicar mensaje en Pulsar
        try:
            import pulsar
            pulsar_client = pulsar.Client('pulsar://52.91.12.250:6650')
            producer = pulsar_client.create_producer('persistent://public/default/ddd-items')
            import json
            producer.send(json.dumps(item).encode('utf-8'))
            pulsar_client.close()
        except Exception as pulsar_error:
            print(f"Error enviando a Pulsar: {pulsar_error}")
        return jsonify(id=item_id, status="saved"), 200
    except Exception as e:
        return jsonify(error=str(e)), 500
    
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(status="ok"), 200

@app.route("/example", methods=["GET"])
def example():
    return jsonify(message="ejemplo de servicio en Flask"), 200

@app.route("/save-in-other-micro", methods=["POST"])
def save_in_other_micro():
    data = request.get_json()
    item = {
        "id": str(uuid.uuid4()),
        "nombre": data.get("nombre", "N/A"),
        "valor": data.get("valor", 0)
    }
    try:
        response = requests.post("http://micro-2.ddd:5000/call-for-other-micro", json=item )
        return jsonify(status="forwarded", response=response.json()), response.status_code
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
