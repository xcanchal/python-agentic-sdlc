import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_sdlc.application.errors import NotFoundError
from agentic_sdlc.infrastructure.database.models import Project


async def create_project(session: AsyncSession, name: str) -> Project:
    new_project = Project(name=name)
    session.add(new_project)
    await session.commit()
    return new_project


async def list_projects(session: AsyncSession) -> Sequence[Project]:
    result = await session.scalars(
        sa.select(Project).order_by(Project.created_at.desc())
    )
    return result.all()


async def get_project(session: AsyncSession, project_id: uuid.UUID) -> Project | None:
    result = await session.get(Project, project_id)
    if result is None:
        raise NotFoundError("Project not found")
    return result
