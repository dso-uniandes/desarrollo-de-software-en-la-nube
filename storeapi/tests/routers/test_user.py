import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    register_user = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@email.com",
        "password1": "StrongPass123",
        "password2": "StrongPass123",
        "city": "Bogotá",
        "country": "Colombia"
    }
    response = await async_client.post("/api/auth/signup", json=register_user)
    assert response.status_code == 201
    assert "User created successfully" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_user_already_exists(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post("/api/auth/signup", json=registered_user)

    assert response.status_code == 400
    assert "User already exists" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        "/api/auth/login",
        data={"username": "test@example.net", "password": "1234"}
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post(
        "/api/auth/login",
        data={"username": registered_user["email"], "password": registered_user["password"], },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    assert "expires_in" in response.json()
