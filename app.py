from typing import Tuple

from flask import Flask, jsonify, request, Response
import mockdb.mockdb_interface as db

app = Flask(__name__)

ENDPOINT_MAIN = "/"
ENDPOINT_MIRROR = "/mirror"
ENDPOINT_USERS = "/users"
ENDPOINT_USERS_BY_ID = "/users/<int:user_id>"

TYPE_USER = "users"


def create_response(
    data: dict = None, status: int = 200, message: str = ""
) -> Tuple[Response, int]:
    """Wraps response in a consistent format throughout the API.

    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response
    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself

    :param data <str> optional data
    :param status <int> optional status code, defaults to 200
    :param message <str> optional message
    :returns tuple of Flask Response and int, which is what flask expects for a response
    """
    if type(data) is not dict and data is not None:
        raise TypeError("Data should be a dictionary 😞")

    response = {
        "code": status,
        "success": 200 <= status < 300,
        "message": message,
        "result": data,
    }
    return jsonify(response), status


"""
~~~~~~~~~~~~ API ~~~~~~~~~~~~
"""


@app.route(ENDPOINT_MAIN)
def hello_world():
    return create_response({"content": "hello world!"})


@app.route("/mirror/<name>")
def mirror(name):
    data = {"name": name}
    return create_response(data)


@app.route(ENDPOINT_USERS, methods=["GET"])
def get_users():
    """
    Query parameters
    ----------------
    team: Get list of users belonging to that team. If no users belong to that team,
          responds with an empty list.
    """
    team = request.args.get("team")
    if team is None:
        return create_response({"users": db.get(TYPE_USER)})
    else:
        return create_response({"users": db.getByTeam(TYPE_USER, team)})


@app.route(ENDPOINT_USERS_BY_ID, methods=["GET"])
def get_user_by_id(user_id):
    user = db.getById(TYPE_USER, user_id)
    if user is None:
        return create_response(
            status=404, message="Could not find a user with id {}".format(user_id)
        )
    return create_response({"user": user})


@app.route(ENDPOINT_USERS, methods=["POST"])
def create_user():
    data = request.get_json()
    if data is None:
        return create_response(status=422, message="No JSON body provided")

    required_keys = ["name", "age", "team"]
    missing_keys = [k for k in required_keys if k not in data]
    if len(missing_keys) > 0:
        msg = "Body lacks the following data: {}".format(", ".join(missing_keys))
        return create_response(status=422, message=msg)

    user_data = {k: data[k] for k in required_keys}
    created_user = db.create(TYPE_USER, user_data)
    return create_response(data={"user": created_user}, status=201)


@app.route(ENDPOINT_USERS_BY_ID, methods=["PUT"])
def update_user_by_id(user_id):
    """
    Only name, age and team can be updated.
    """
    data = request.get_json()
    allowed_keys = ["name", "age", "team"]
    user_data = {k: data[k] for k in allowed_keys if k in data}
    updated_user = db.updateById(TYPE_USER, user_id, user_data)
    if updated_user is None:
        return create_response(
            status=404, message="Could not find a user with id {}".format(user_id)
        )
    return create_response({"user": updated_user})


@app.route(ENDPOINT_USERS_BY_ID, methods=["DELETE"])
def delete_user_by_id(user_id):
    if db.getById(TYPE_USER, user_id) is None:
        return create_response(
            status=404, message="Could not find a user with id {}".format(user_id)
        )
    db.deleteById(TYPE_USER, user_id)
    return create_response(message="Deleted user with id {}".format(user_id))


"""
~~~~~~~~~~~~ END API ~~~~~~~~~~~~
"""
if __name__ == "__main__":
    app.run(debug=True)
