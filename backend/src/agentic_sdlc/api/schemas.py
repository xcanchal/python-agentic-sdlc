import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from agentic_sdlc.domain.limits import PROJECT_NAME_MAX_LENGTH


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=PROJECT_NAME_MAX_LENGTH)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_at: datetime
