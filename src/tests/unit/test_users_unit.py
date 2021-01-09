import json
from datetime import datetime

import pytest

import src.api.users.views


def test_add_user(test_app, monkeypatch):
    def mock_get_user_by_email(email):
        return None

    def mock_add_user(username, email):
        return True

    monkeypatch.setattr(
        src.api.users.views, "get_user_by_email", mock_get_user_by_email
    )
    monkeypatch.setattr(src.api.users.views, "add_user", mock_add_user)

    client = test_app.test_client()
    resp = client.post(
        "/users",
        data=json.dumps({"username": "testuser", "email": "testuser@test.com"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 201
    assert "testuser@test.com was added!" in data["message"]


def test_add_user_invalid_json(test_app):
    client = test_app.test_client()
    resp = client.post(
        "/users",
        data=json.dumps({}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_invalid_json_keys(test_app, monkeypatch):
    client = test_app.test_client()
    resp = client.post(
        "/users",
        data=json.dumps({"email": "testuser@test.com"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_duplicate_email(test_app, monkeypatch):
    def mock_get_user_by_email(email):
        return True

    def mock_add_user(username, email):
        return True

    monkeypatch.setattr(
        src.api.users.views, "get_user_by_email", mock_get_user_by_email
    )
    monkeypatch.setattr(src.api.users.views, "add_user", mock_add_user)
    client = test_app.test_client()
    client.post(
        "/users",
        data=json.dumps({"username": "bob", "email": "bob@bob.com"}),
        content_type="application/json",
    )
    resp = client.post(
        "/users",
        data=json.dumps({"username": "bob", "email": "bob@bob.com"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert "Sorry. That email already exists." in data["message"]


def test_single_user(test_app, monkeypatch):
    def mock_get_user_by_id(user_id):
        return {
            "id": 1,
            "username": "musa",
            "email": "musa@musa.com",
            "created_date": datetime.now(),
        }

    monkeypatch.setattr(src.api.users.views, "get_user_by_id", mock_get_user_by_id)
    client = test_app.test_client()
    resp = client.get("/users/1")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert "musa" in data["username"]
    assert "musa@musa.com" in data["email"]


def test_single_user_incorrect_id(test_app, monkeypatch):
    def mock_get_user_by_id(user_id):
        return None

    monkeypatch.setattr(src.api.users.views, "get_user_by_id", mock_get_user_by_id)
    client = test_app.test_client()
    resp = client.get("/users/999")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 404
    assert "User 999 does not exist" in data["message"]


def test_all_users(test_app, monkeypatch):
    def mock_get_all_users():
        return [
            {
                "id": 1,
                "username": "bob",
                "email": "bob@bob.org",
                "created_date": datetime.now(),
            },
            {
                "id": 1,
                "username": "tim",
                "email": "tim@tim.com",
                "created_date": datetime.now(),
            },
        ]

    monkeypatch.setattr(src.api.users.views, "get_all_users", mock_get_all_users)
    client = test_app.test_client()
    resp = client.get("/users")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert len(data) == 2
    assert "bob" in data[0]["username"]
    assert "bob@bob.org" in data[0]["email"]
    assert "tim" in data[1]["username"]
    assert "tim@tim.com" in data[1]["email"]


def test_remove_user(test_app, monkeypatch):
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self

    def mock_get_user_by_id(user_id):
        d = AttrDict()
        d.update(
            {"id": 1, "username": "user-to-be-removed", "email": "remove-me@remove.com"}
        )
        return d

    def mock_delete_user(user):
        return True

    monkeypatch.setattr(src.api.users.views, "get_user_by_id", mock_get_user_by_id)
    monkeypatch.setattr(src.api.users.views, "delete_user", mock_delete_user)
    client = test_app.test_client()
    resp_two = client.delete("/users/1")
    data = json.loads(resp_two.data.decode())
    assert resp_two.status_code == 200
    assert "remove-me@remove.com was removed!" in data["message"]


def test_remove_user_incorrect_id(test_app, monkeypatch):
    def mock_get_user_by_id(user_id):
        return None

    monkeypatch.setattr(src.api.users.views, "get_user_by_id", mock_get_user_by_id)
    client = test_app.test_client()
    resp = client.delete("/users/999")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 404
    assert "User 999 does not exist" in data["message"]


@pytest.mark.parametrize(
    "user_id, payload, status_code, message",
    [
        [1, {}, 400, "Input payload validation failed"],
        [1, {"email": "me@me.com"}, 400, "Input payload validation failed"],
        [
            999,
            {"username": "me", "email": "me@me.com"},
            404,
            "User 999 does not exist",
        ],
    ],
)
def test_update_user_invalid(
    test_app, monkeypatch, user_id, payload, status_code, message
):
    def mock_get_user_by_id(user_id):
        return None

    monkeypatch.setattr(src.api.users.views, "get_user_by_id", mock_get_user_by_id)
    client = test_app.test_client()
    resp = client.put(
        f"/users/{user_id}",
        data=json.dumps(payload),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == status_code
    assert message in data["message"]


def test_update_user_duplicate_email(test_app, monkeypatch):
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self

    def mock_get_user_by_id(user_id):
        d = AttrDict()
        d.update({"id": 1, "username": "me", "email": "me@me.com"})
        return d

    def mock_update_user(user, username, email):
        return True

    def mock_get_user_by_email(email):
        return True

    monkeypatch.setattr(src.api.users.views, "get_user_by_id", mock_get_user_by_id)
    monkeypatch.setattr(
        src.api.users.views, "get_user_by_email", mock_get_user_by_email
    )
    monkeypatch.setattr(src.api.users.views, "update_user", mock_update_user)
    client = test_app.test_client()
    resp = client.put(
        "/users/1",
        data=json.dumps({"username": "me", "email": "me@me.com"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert "Sorry. That email already exists." in data["message"]
