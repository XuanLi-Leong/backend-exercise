
# pytest automatically injects fixtures
# that are defined in conftest.py
# in this case, client is injected
def test_index(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json["result"]["content"] == "hello world!"


def test_mirror(client):
    res = client.get("/mirror/Tim")
    assert res.status_code == 200
    assert res.json["result"]["name"] == "Tim"


def test_get_users(client):
    res = client.get("/users")
    assert res.status_code == 200

    res_users = res.json["result"]["users"]
    assert len(res_users) == 4
    assert res_users[0]["name"] == "Aria"


def tests_get_users_with_team(client):
    res = client.get("/users?team=LWB")
    assert res.status_code == 200

    res_users = res.json["result"]["users"]
    assert len(res_users) == 2
    assert res_users[1]["name"] == "Tim"


def test_get_user_id(client):
    # Test successful request
    res = client.get("/users/1")
    assert res.status_code == 200

    res_user = res.json["result"]["user"]
    assert res_user["name"] == "Aria"
    assert res_user["age"] == 19

    # Test bad request
    res = client.get("/users/0")
    assert res.status_code == 404
    assert len(res.json["message"]) > 0


def test_create_user(client):
    # Test successful request
    body = {"name": "Lato", "age": 28, "team": "C2TC"}
    res = client.post("/users", json=body)
    assert res.status_code == 201

    res_user = res.json["result"]["user"]
    assert res_user["name"] == "Lato"
    assert res_user["id"] == 5

    # Test bad request
    body = {"name": "Lato", "age": 28}
    res = client.post("/users", json=body)
    assert res.status_code == 422
    assert len(res.json["message"]) > 0


def test_update_user_by_id(client):
    body = {"name": "Angel"}

    # Test successful request
    res = client.put("/users/1", json=body)
    assert res.status_code == 200

    res_user = res.json["result"]["user"]
    assert res_user["name"] == "Angel"
    assert res_user["age"] == 19

    # Test bad request
    res = client.put("/users/0", json=body)
    assert res.status_code == 404
    assert len(res.json["message"]) > 0


def test_delete_user_by_id(client):
    # Test successful request
    res = client.delete("/users/1")
    assert res.status_code == 200
    assert len(res.json["message"]) > 0

    # Test bad request
    res = client.delete("/users/1")
    assert res.status_code == 404
    assert len(res.json["message"]) > 0
