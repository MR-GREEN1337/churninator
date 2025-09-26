from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.settings import get_settings
import ssl
from functools import lru_cache
from typing import Union

settings = get_settings()

# --- SSL Configuration ---
connect_args: dict[str, Union[ssl.SSLContext, str]] = {}
if settings.DB_SSL_MODE != "disable":
    ssl_context = ssl.create_default_context()
    # In prod, you'd configure this more strictly, e.g., with ca_certs
    connect_args["ssl"] = ssl_context
else:
    connect_args["ssl"] = "disable"

# --- SQLAlchemy Async Engine with Connection Pooling ---
engine = create_async_engine(
    url=str(settings.DATABASE_URL),
    echo=settings.DB_ECHO_LOG,
    pool_size=settings.POSTGRES_POOL_SIZE,
    max_overflow=settings.POSTGRES_MAX_OVERFLOW,
    pool_pre_ping=True,
    connect_args=connect_args,
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@lru_cache
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to provide a database session per request."""
    async with AsyncSessionLocal() as session:
        yield session
