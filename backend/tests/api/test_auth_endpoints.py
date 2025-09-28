import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.db.models.user import User

pytestmark = pytest.mark.asyncio


async def test_register_user_success(
    test_client: AsyncClient, db_session: AsyncSession
):
    """Test successful user registration."""
    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "newpassword",  # pragma: allowlist secret
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    # Check user is actually in the DB
    user = await db_session.get(User, data["id"])
    assert user is not None


async def test_register_duplicate_email(test_client: AsyncClient, test_user: User):
    """Test registration with an email that already exists."""
    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "password",  # pragma: allowlist secret
        },
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


async def test_get_current_user_me(test_client: AsyncClient, test_user: User):
    """Test the /users/me endpoint with an authenticated user."""
    response = await test_client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == str(test_user.id)
