import os
from flask import Flask, jsonify, request

from core.db import (
    init_db,
    list_clients,
    get_client,
    add_client,
    generate_program_for_client,
)

app = Flask(__name__)

# Initialize DB/schema on import/startup
init_db()


@app.route("/clients", methods=["GET"])
def clients_get():
    return jsonify(list_clients()), 200


@app.route("/clients/<string:name>", methods=["GET"])
def clients_get_one(name):
    c = get_client(name)
    if not c:
        return jsonify({"error": "client not found"}), 404
    return jsonify(c), 200


@app.route("/clients", methods=["POST"])
def clients_post():
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("name")
    age = data.get("age")
    if not name:
        return jsonify({"error": "'name' is required"}), 400
    try:
        add_client(name, age)
    except Exception as e:
        # sqlite3.IntegrityError when duplicate name; return 409
        return jsonify({"error": "client already exists"}), 409
    return jsonify({"message": "client added", "name": name}), 201


@app.route("/clients/<string:name>/generate_program", methods=["POST"])
def clients_generate(name):
    program = generate_program_for_client(name)
    if not program:
        return jsonify({"error": "client not found"}), 404
    return jsonify({"client": name, "program": program}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
