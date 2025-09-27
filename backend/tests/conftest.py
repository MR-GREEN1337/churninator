# backend/tests/conftest.py
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

import dramatiq
from dramatiq.brokers.stub import StubBroker

from backend.src.main import app
from backend.src.core.settings import get_settings
from backend.src.db.postgresql import get_session
from backend.src.db.models.user import User, UserCreate
from backend.src.core.security import get_password_hash


# --- Broker Mocking ---
@pytest.fixture(scope="session")
def mock_broker() -> Generator[StubBroker, None, None]:
    """Sets up a stub Dramatiq broker for the entire test session."""
    broker = StubBroker()
    broker.emit_after("process_boot")
    dramatiq.set_broker(broker)
    yield broker
    broker.flush_all()


# --- Database Fixtures for Isolated Testing ---
TEST_DATABASE_URL = str(get_settings().DATABASE_URL) + "_test"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncTestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency override for getting a test database session."""
    async with AsyncTestingSessionLocal() as session:
        yield session


# Apply the override to our FastAPI app
app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture(scope="session")
async def setup_database():
    """Creates and drops the test database tables for the session."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Yields a new transaction-wrapped session for each test function."""
    async with AsyncTestingSessionLocal() as session:
        await session.begin_nested()
        yield session
        await session.rollback()


# --- API Test Client ---
@pytest_asyncio.fixture(scope="function")
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Yields an HTTPX async client for making API requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# --- User & Data Fixtures ---
@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Creates a test user in the database for authentication mocking."""
    user_in = UserCreate(email="test@example.com", password="password")
    hashed_password = get_password_hash(user_in.password)
    db_user = User.model_validate(user_in, update={"hashed_password": hashed_password})
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user
