import uuid
from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import JSONB
import datetime as dt


class ReportBase(SQLModel):
    target_url: str
    task_prompt: str


class Report(ReportBase, table=True):  # type: ignore[call-arg]
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    status: str = Field(default="PENDING", index=True)
    # Use `Dict[str, Any]` for type-safe JSONB
    result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow, nullable=False)
    updated_at: dt.datetime = Field(
        default_factory=dt.datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": dt.datetime.utcnow},
    )


class ReportCreate(ReportBase):
    pass  # This will be the Pydantic model for API input


class ReportRead(ReportBase):
    id: uuid.UUID
    status: str
    created_at: dt.datetime
