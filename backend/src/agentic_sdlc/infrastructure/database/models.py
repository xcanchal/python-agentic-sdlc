import uuid
from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import DateTime, String, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from agentic_sdlc.domain.limits import PROJECT_NAME_MAX_LENGTH


class Base(DeclarativeBase):
    type_annotation_map: ClassVar[dict[Any, Any]] = {datetime: DateTime(timezone=True)}


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(PROJECT_NAME_MAX_LENGTH))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
