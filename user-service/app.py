from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Starts empty - users are created at runtime via POST /users.
USERS = {}
next_user_id = 1


@app.route("/")
def home():
    return jsonify(service="user-service", status="running")


@app.route("/health")
def health():
    return jsonify(status="UP"), 200


# ---- Create ----
@app.route("/users", methods=["POST"])
def create_user():
    global next_user_id
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        abort(400, description="Both 'name' and 'email' are required")

    user = {"id": next_user_id, "name": name, "email": email}
    USERS[next_user_id] = user
    next_user_id += 1
    return jsonify(user), 201


# ---- Read (all) ----
@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(list(USERS.values()))


# ---- Read (one) ----
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = USERS.get(user_id)
    if not user:
        abort(404, description="User not found")
    return jsonify(user)


# ---- Update ----
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = USERS.get(user_id)
    if not user:
        abort(404, description="User not found")

    data = request.get_json(force=True, silent=True) or {}
    if "name" in data:
        user["name"] = data["name"]
    if "email" in data:
        user["email"] = data["email"]

    return jsonify(user)


# ---- Delete ----
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = USERS.pop(user_id, None)
    if not user:
        abort(404, description="User not found")
    return jsonify(message=f"User {user_id} deleted"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
