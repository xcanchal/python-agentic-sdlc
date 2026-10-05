import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_sdlc.application.errors import NotFoundError
from agentic_sdlc.application.projects import get_project
from agentic_sdlc.infrastructure.database.models import WorkItem


async def create_work_item(
    session: AsyncSession, *, project_id: uuid.UUID, title: str, description: str
) -> WorkItem:
    await get_project(session, project_id)

    new_work_item = WorkItem(
        project_id=project_id, title=title, description=description
    )
    session.add(new_work_item)
    await session.commit()
    return new_work_item


async def list_work_items(
    session: AsyncSession, project_id: uuid.UUID
) -> Sequence[WorkItem]:
    await get_project(session, project_id)

    result = await session.scalars(
        sa.select(WorkItem)
        .where(WorkItem.project_id == project_id)
        .order_by(WorkItem.created_at.desc())
    )

    return result.all()


async def get_work_item(session: AsyncSession, work_item_id: uuid.UUID) -> WorkItem:
    result = await session.get(WorkItem, work_item_id)
    if result is None:
        raise NotFoundError("Work item not found")
    return result
