import uuid
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Column, Relationship
from sqlalchemy.dialects.postgresql import JSONB
import datetime as dt

if TYPE_CHECKING:
    from .user import User


class AgentRunBase(SQLModel):
    target_url: str
    task_prompt: str

    favicon_url: Optional[str] = Field(default=None)


class AgentRun(AgentRunBase, table=True):  # type: ignore[call-arg]
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    status: str = Field(default="PENDING", index=True)

    # Store the step-by-step log of the agent's run
    run_log: Optional[List[Dict[str, Any]]] = Field(
        default=None, sa_column=Column(JSONB)
    )

    # Final result/summary from the agent
    final_result: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB)
    )

    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)

    # Add a foreign key to the user who initiated the run
    owner_id: uuid.UUID = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="runs")


class AgentRunCreate(AgentRunBase):
    pass


class AgentRunRead(AgentRunBase):
    id: uuid.UUID
    status: str
    created_at: dt.datetime
