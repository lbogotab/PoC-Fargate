from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(status="ok"), 200

@app.route("/example", methods=["GET"])
def example():
    return jsonify(message="ejemplo de servicio en Flask"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# Action ECR1