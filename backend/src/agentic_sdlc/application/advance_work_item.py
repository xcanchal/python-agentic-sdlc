import uuid

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_sdlc.application.errors import InvalidStageTransitionError
from agentic_sdlc.application.work_items import get_work_item
from agentic_sdlc.domain.enums import StageRunStatus
from agentic_sdlc.domain.stages import next_stage
from agentic_sdlc.infrastructure.database.models import StageRun, WorkItem


async def advance_work_item(
    session: AsyncSession, *, work_item_id: uuid.UUID
) -> WorkItem:
    work_item = await get_work_item(session, work_item_id)

    following_stage = next_stage(work_item.current_stage)

    completed_run_id = await session.scalar(
        sa.select(StageRun.id)
        .where(
            StageRun.work_item_id == work_item_id,
            StageRun.stage == work_item.current_stage,
            StageRun.status == StageRunStatus.COMPLETED,
        )
        .limit(1)
    )

    if completed_run_id is None:
        raise InvalidStageTransitionError("Current stage has no completed run")

    work_item.current_stage = following_stage
    await session.commit()

    return work_item
