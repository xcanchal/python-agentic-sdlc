from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_sdlc.domain.enums import Stage, StageRunStatus
from agentic_sdlc.infrastructure.database.models import StageRun, WorkItem


class TestStageRun:
    async def test_new_run_gets_defaults(
        self, session: AsyncSession, work_item: WorkItem
    ) -> None:
        run = StageRun(
            work_item_id=work_item.id, stage=Stage.RESEARCH, model="test-model"
        )
        session.add(run)
        await session.commit()
        run_id = run.id
        session.expire_all()

        stored_stage_run = await session.get(StageRun, run_id)

        assert stored_stage_run is not None
        assert stored_stage_run.status == StageRunStatus.RUNNING
        assert stored_stage_run.model == "test-model"
        assert stored_stage_run.stage == Stage.RESEARCH
        assert stored_stage_run.error is None
        assert stored_stage_run.completed_at is None

    async def test_failed_run_keeps_error(
        self, session: AsyncSession, work_item: WorkItem
    ) -> None:
        completed_at = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)

        run = StageRun(
            work_item_id=work_item.id,
            stage=Stage.RESEARCH,
            model="test-model",
            status=StageRunStatus.FAILED,
            error="Provider timeout",
            completed_at=completed_at,
        )
        session.add(run)
        await session.commit()
        run_id = run.id
        session.expire_all()

        stored_stage_run = await session.get(StageRun, run_id)

        assert stored_stage_run is not None
        assert stored_stage_run.status == StageRunStatus.FAILED
        assert stored_stage_run.error == "Provider timeout"
        assert stored_stage_run.completed_at == completed_at

    async def test_deleting_work_item_deletes_its_runs(
        self, session: AsyncSession, work_item: WorkItem
    ) -> None:
        session.add(
            StageRun(
                work_item_id=work_item.id, stage=Stage.RESEARCH, model="test-model"
            )
        )
        await session.commit()

        await session.delete(work_item)

        await session.commit()

        remaining_runs = (await session.scalars(sa.select(StageRun))).all()
        assert remaining_runs == []


class TestArtifact:
    async def test_run_has_several_artifacts(
        self, session: AsyncSession, work_item: WorkItem
    ) -> None:
        pass

    async def test_artifacts_link_the_right_work_item(
        self, session: AsyncSession, work_item: WorkItem
    ) -> None:
        pass

    async def test_deleting_run_deletes_artifacts(
        self, session: AsyncSession, work_item: WorkItem
    ) -> None:
        pass
