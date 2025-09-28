# backend/src/db/models/user.py
import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
import datetime as dt

if TYPE_CHECKING:
    from .agent_run import AgentRun
    from .oauth_account import OAuthAccount


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = Field(default=True)


class User(UserBase, table=True):  # type: ignore[call-arg]
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: Optional[str] = Field(default=None)
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    run_count: int = Field(default=0, nullable=False)

    # --- START STRIPE FIELDS ---
    stripe_customer_id: Optional[str] = Field(default=None, unique=True, index=True)
    subscription_id: Optional[str] = Field(default=None, unique=True)
    subscription_status: Optional[str] = Field(
        default=None
    )  # e.g., "active", "canceled", "past_due"
    plan_id: Optional[str] = Field(default=None)
    subscription_ends_at: Optional[dt.datetime] = Field(default=None)
    # --- END STRIPE FIELDS ---

    runs: List["AgentRun"] = Relationship(back_populates="owner")
    oauth_accounts: List["OAuthAccount"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: Optional[str] = None


class UserRead(UserBase):
    id: uuid.UUID
    # Expose subscription status to the frontend
    subscription_status: Optional[str] = None


class UserUpdate(SQLModel):
    full_name: Optional[str] = None
