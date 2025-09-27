import uuid
from typing import Optional, TYPE_CHECKING, List
from sqlmodel import Field, SQLModel, Relationship
import datetime as dt

if TYPE_CHECKING:
    from .agent_run import AgentRun


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):  # type: ignore[call-arg]
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)

    # Useful for analytics, usage-based billing, or feature flagging.
    run_count: int = Field(default=0, nullable=False)

    # Back-relationship to agent runs
    runs: List["AgentRun"] = Relationship(back_populates="owner")


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: uuid.UUID
