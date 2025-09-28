import uuid
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Column, Relationship
from sqlalchemy.dialects.postgresql import JSONB
import datetime as dt
from pydantic import BaseModel

if TYPE_CHECKING:
    from .user import User

# --- Pydantic models defining the JSON structure for logs and reports ---


class RunStep(BaseModel):
    """Defines the structure for a single step in the agent's log."""

    step: int
    thought: str
    action: str
    screenshot_path: str
    observation: str
    friction_score: int


class FrictionPoint(BaseModel):
    """Defines the structure for a single friction point in the final report."""

    step: int
    screenshot_path: str
    description: str
    recommendation: str


class FinalReport(BaseModel):
    """Defines the structure of the final AI-generated JSON report."""

    summary: str
    positive_points: List[str]
    friction_points: List[FrictionPoint]


# --- SQLModel Database Models ---


class AgentRunBase(SQLModel):
    target_url: str
    task_prompt: str
    favicon_url: Optional[str] = Field(default=None)


class AgentRun(AgentRunBase, table=True):  # type: ignore[call-arg]
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    status: str = Field(default="PENDING", index=True)
    run_log: Optional[List[Dict[str, Any]]] = Field(
        default=None, sa_column=Column(JSONB)
    )
    final_result: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB)
    )
    report_path: Optional[str] = Field(default=None)
    # --- ADDED: Field to store the selected keyframe step numbers ---
    keyframe_indices: Optional[List[int]] = Field(default=None, sa_column=Column(JSONB))
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    owner_id: uuid.UUID = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="runs")


class AgentRunCreate(AgentRunBase):
    pass


class AgentRunRead(AgentRunBase):
    id: uuid.UUID
    status: str
    created_at: dt.datetime
    final_result: Optional[Dict[str, Any]] = None
    # Expose the report path to the frontend
    report_path: Optional[str] = None
