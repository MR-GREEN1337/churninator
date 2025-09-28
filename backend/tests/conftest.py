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

# --- App and Dependency Imports ---
from backend.src.main import app
from backend.src.core.settings import get_settings
from backend.src.db.postgresql import get_session
from backend.src.db.models.user import User, UserCreate
from backend.src.core.security import get_password_hash
from backend.src.api.v1.dependencies import get_current_user


# --- Broker Mocking ---
@pytest.fixture(scope="session")
def mock_broker() -> Generator[StubBroker, None, None]:
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
    async with AsyncTestingSessionLocal() as session:
        yield session


# --- START: Authentication Override ---
# This is the key to testing protected endpoints.
async def override_get_current_user(
    test_user: User = pytest.lazy_fixture("test_user"),
) -> User:
    """Dependency override to provide a mock authenticated user."""
    return test_user


# Apply the dependency overrides to our FastAPI app for all tests.
app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_current_user] = override_get_current_user
# --- END: Authentication Override ---


@pytest_asyncio.fixture(scope="session")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncTestingSessionLocal() as session:
        await session.begin_nested()
        yield session
        await session.rollback()


# --- API Test Client ---
@pytest_asyncio.fixture(scope="function")
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Yields an HTTPX async client for making API requests as the test_user."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# --- User & Data Fixtures ---
@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    user_in = UserCreate(
        email="test@example.com",
        password="password",  # pragma: allowlist secret
        full_name="Test User",  # pragma: allowlist secret
    )
    if not user_in.password:
        raise ValueError("Password is required for test_user fixture")
    hashed_password = get_password_hash(user_in.password)
    db_user = User.model_validate(user_in, update={"hashed_password": hashed_password})
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user
