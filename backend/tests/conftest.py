from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
import dramatiq
from dramatiq.brokers.stub import StubBroker

from backend.src.main import app
from backend.src.core.settings import get_settings
from backend.src.db.postgresql import get_session
from backend.src.db.models.user import User, UserCreate
from backend.src.core.security import get_password_hash
from backend.src.api.v1.dependencies import get_current_user

# Import all models
from backend.src.db.models import User, AgentRun, OAuthAccount, Report  # noqa


# Configure pytest-asyncio to use function scope by default
@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for the session."""
    import asyncio

    return asyncio.get_event_loop_policy()


# --- Broker Mocking ---
@pytest.fixture(scope="session")
def mock_broker():
    broker = StubBroker()
    broker.emit_after("process_boot")
    dramatiq.set_broker(broker)
    yield broker
    broker.flush_all()


# --- Database Configuration ---
settings = get_settings()

# Create engine with proper async configuration
test_engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=False,
    pool_pre_ping=True,
    future=True,
    # Critical: disable statement cache for tests
    connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0},
)

# Use async_sessionmaker instead of sessionmaker
AsyncTestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,  # Important for test isolation
)


# --- Database Fixtures ---
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables once for the session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a clean transactional database session for each test.
    Changes are rolled back after each test.
    """
    async with AsyncTestingSessionLocal() as session:
        async with session.begin():
            yield session
            # Rollback happens automatically when context exits


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user for each test function."""
    from uuid import uuid4

    # Use unique email per test to avoid conflicts
    unique_email = f"test-{uuid4().hex[:8]}@example.com"

    user_in = UserCreate(
        email=unique_email,
        password="testpassword123",  # pragma: allowlist secret
        full_name="Test User",
    )

    if not user_in.password:
        raise ValueError("password can't be None")

    hashed_password = get_password_hash(user_in.password)
    db_user = User.model_validate(user_in, update={"hashed_password": hashed_password})

    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)

    return db_user


def create_auth_override(user: User):
    """Create an auth override function for a specific user."""

    async def override_get_current_user() -> User:
        return user

    return override_get_current_user


@pytest_asyncio.fixture(scope="function")
async def test_client(
    db_session: AsyncSession, test_user: User
) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an authenticated test client that shares the same
    database session with the test.
    """

    # Critical: Override get_session to return the test's db_session
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = create_auth_override(test_user)

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://test", follow_redirects=True
        ) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


# --- Additional Test Utilities ---
@pytest.fixture
def anyio_backend():
    """Configure anyio to use asyncio."""
    return "asyncio"


@pytest_asyncio.fixture
async def mock_playwright_page():
    """Mock Playwright page for worker tests."""
    from unittest.mock import AsyncMock

    mock_page = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b"fake_screenshot_data")
    mock_page.goto = AsyncMock()
    mock_page.url = "https://example.com"

    return mock_page
