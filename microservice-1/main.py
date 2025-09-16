from flask import Flask, jsonify

app = Flask(__name__)

import boto3
import uuid
import os
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
        return jsonify(id=item_id, status="saved"), 200
    except Exception as e:
        return jsonify(error=str(e)), 500
    
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(status="ok"), 200

@app.route("/example", methods=["GET"])
def example():
    return jsonify(message="ejemplo de servicio en Flask"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
