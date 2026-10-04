import enum
import uuid
from datetime import datetime
from typing import Annotated, Any, ClassVar

from sqlalchemy import DateTime, ForeignKey, String, Text, func, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from agentic_sdlc.domain.enums import Stage, WorkItemStatus
from agentic_sdlc.domain.limits import (
    PROJECT_NAME_MAX_LENGTH,
    WORK_ITEM_TITLE_MAX_LENGTH,
)


class Base(DeclarativeBase):
    type_annotation_map: ClassVar[dict[Any, Any]] = {
        datetime: DateTime(timezone=True),
        enum.Enum: SAEnum(enum.Enum, native_enum=False, length=32),
    }


UuidPk = Annotated[
    uuid.UUID,
    mapped_column(primary_key=True, server_default=text("gen_random_uuid()")),
]
CreatedAt = Annotated[datetime, mapped_column(server_default=func.now())]


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UuidPk]
    name: Mapped[str] = mapped_column(String(PROJECT_NAME_MAX_LENGTH))
    created_at: Mapped[CreatedAt]


class WorkItem(Base):
    __tablename__ = "work_items"
    __mapper_args__ = {"eager_defaults": True}  # noqa: RUF012

    id: Mapped[UuidPk]
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(WORK_ITEM_TITLE_MAX_LENGTH))
    description: Mapped[str] = mapped_column(Text)
    current_stage: Mapped[Stage] = mapped_column(server_default=Stage.RESEARCH.value)
    status: Mapped[WorkItemStatus] = mapped_column(
        server_default=WorkItemStatus.ACTIVE.value
    )
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
