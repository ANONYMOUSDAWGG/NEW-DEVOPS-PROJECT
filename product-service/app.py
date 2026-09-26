from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Starts empty - products are created at runtime via POST /products.
PRODUCTS = {}
next_product_id = 1


@app.route("/")
def home():
    return jsonify(service="product-service", status="running")


@app.route("/health")
def health():
    return jsonify(status="UP"), 200


# ---- Create ----
@app.route("/products", methods=["POST"])
def create_product():
    global next_product_id
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("name")
    price = data.get("price")

    if not name or price is None:
        abort(400, description="Both 'name' and 'price' are required")

    product = {"id": next_product_id, "name": name, "price": price}
    PRODUCTS[next_product_id] = product
    next_product_id += 1
    return jsonify(product), 201


# ---- Read (all) ----
@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(list(PRODUCTS.values()))


# ---- Read (one) ----
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = PRODUCTS.get(product_id)
    if not product:
        abort(404, description="Product not found")
    return jsonify(product)


# ---- Update ----
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = PRODUCTS.get(product_id)
    if not product:
        abort(404, description="Product not found")

    data = request.get_json(force=True, silent=True) or {}
    if "name" in data:
        product["name"] = data["name"]
    if "price" in data:
        product["price"] = data["price"]

    return jsonify(product)


# ---- Delete ----
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = PRODUCTS.pop(product_id, None)
    if not product:
        abort(404, description="Product not found")
    return jsonify(message=f"Product {product_id} deleted"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
