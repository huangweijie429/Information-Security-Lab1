"""Functional + security regression tests for the Work 1 API."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

CREDS = {"username": "admin", "password": "Admin123!"}


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def token(client):
    r = client.post("/auth/login", json=CREDS)
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_login_returns_jwt(client):
    r = client.post("/auth/login", json=CREDS)
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"].count(".") == 2


def test_login_rejects_wrong_password(client):
    r = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    assert r.status_code == 401


def test_login_rejects_sqli_payload(client):
    payload = {"username": "admin' OR '1'='1", "password": "x"}
    r = client.post("/auth/login", json=payload)
    assert r.status_code in (401, 422)


def test_data_requires_token(client):
    assert client.get("/api/data").status_code == 401


def test_data_rejects_garbage_token(client):
    r = client.get("/api/data", headers={"Authorization": "Bearer not-a-jwt"})
    assert r.status_code == 401


def test_data_with_token(client, token):
    r = client.get("/api/data", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    rows = r.json()
    assert isinstance(rows, list) and rows
    assert {"id", "author", "title", "body"} <= set(rows[0])


def test_xss_payload_is_escaped(client, token):
    r = client.get(
        "/api/data", params={"q": "Notes"}, headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    body = r.json()[0]["body"]
    assert "<b>" not in body
    assert "&lt;b&gt;" in body


def test_me(client, token):
    r = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["username"] == "admin"


def test_sqli_in_search_is_parameterized(client, token):
    r = client.get(
        "/api/data",
        params={"q": "' OR 1=1 --"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json() == []
