import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_login_refresh_logout_flow(client: AsyncClient) -> None:
    register_payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "supersecret123",
        "role": "ANALYST",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201
    body = register_response.json()
    assert body["username"] == "alice"
    assert body["role"] == "ANALYST"

    login_response = await client.post(
        "/api/v1/auth/login", json={"username": "alice", "password": "supersecret123"}
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    me_response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "alice"

    refresh_response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert new_tokens["access_token"] != tokens["access_token"]

    logout_response = await client.post(
        "/api/v1/auth/logout", json={"refresh_token": new_tokens["refresh_token"]}
    )
    assert logout_response.status_code == 204


@pytest.mark.asyncio
async def test_login_with_invalid_credentials_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login", json={"username": "ghost", "password": "wrong-password"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_duplicate_username_returns_409(client: AsyncClient) -> None:
    payload = {
        "username": "bob",
        "email": "bob@example.com",
        "password": "supersecret123",
    }
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second_payload = {**payload, "email": "bob2@example.com"}
    second = await client.post("/api/v1/auth/register", json=second_payload)
    assert second.status_code == 409
