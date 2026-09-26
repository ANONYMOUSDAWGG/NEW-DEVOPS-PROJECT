import os
from flask import Flask, jsonify, request, abort
import requests

app = Flask(__name__)

# These default hostnames match the service names in docker-compose.yml.
# Docker's internal DNS resolves "user-service" / "product-service" to the
# right container automatically, so no hardcoded IPs are needed.
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://user-service:5001")
PRODUCT_SERVICE_URL = os.environ.get("PRODUCT_SERVICE_URL", "http://product-service:5002")

ORDERS = []
next_order_id = 1


@app.route("/")
def home():
    return jsonify(service="order-service", status="running")


@app.route("/health")
def health():
    return jsonify(status="UP"), 200


@app.route("/orders", methods=["POST"])
def create_order():
    global next_order_id
    data = request.get_json(force=True, silent=True) or {}
    user_id = data.get("user_id")
    product_id = data.get("product_id")

    if user_id is None or product_id is None:
        abort(400, description="user_id and product_id are required")

    # --- Service-to-service call #1: validate the user ---
    try:
        user_resp = requests.get(f"{USER_SERVICE_URL}/users/{user_id}", timeout=5)
    except requests.exceptions.RequestException:
        abort(503, description="user-service is unavailable")
    if user_resp.status_code != 200:
        abort(404, description="User not found in user-service")
    user = user_resp.json()

    # --- Service-to-service call #2: validate the product ---
    try:
        product_resp = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}", timeout=5)
    except requests.exceptions.RequestException:
        abort(503, description="product-service is unavailable")
    if product_resp.status_code != 200:
        abort(404, description="Product not found in product-service")
    product = product_resp.json()

    order = {
        "order_id": next_order_id,
        "user": user,
        "product": product,
        "status": "CONFIRMED",
    }
    ORDERS.append(order)
    next_order_id += 1
    return jsonify(order), 201


@app.route("/orders")
def get_orders():
    return jsonify(ORDERS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
