import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from agentic_sdlc.domain.enums import Stage, WorkItemStatus
from agentic_sdlc.domain.limits import (
    PROJECT_NAME_MAX_LENGTH,
    WORK_ITEM_DESCRIPTION_MAX_LENGTH,
    WORK_ITEM_TITLE_MAX_LENGTH,
)


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=PROJECT_NAME_MAX_LENGTH)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_at: datetime


class WorkItemCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=WORK_ITEM_TITLE_MAX_LENGTH)
    description: str = Field(min_length=1, max_length=WORK_ITEM_DESCRIPTION_MAX_LENGTH)


class WorkItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str
    current_stage: Stage
    status: WorkItemStatus
    created_at: datetime
    updated_at: datetime
