# backend/src/db/models/oauth_account.py
import uuid
from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .user import User


class OAuthAccount(SQLModel, table=True):  # type: ignore[call-arg]
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    provider: str  # e.g., 'google', 'github'
    provider_user_id: str  # The user's ID on the provider's system
    access_token: str  # Can be useful for API calls on behalf of the user

    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="oauth_accounts")
