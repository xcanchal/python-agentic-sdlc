from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_sdlc.domain.enums import ArtifactKind, Stage, StageRunStatus
from agentic_sdlc.infrastructure.database.models import Artifact, StageRun, WorkItem


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
        self, session: AsyncSession, stage_run: StageRun
    ) -> None:
        artifact_1 = Artifact(
            stage_run_id=stage_run.id,
            kind=ArtifactKind.PRD,
            content="This is a PRD artifact",
        )
        artifact_2 = Artifact(
            stage_run_id=stage_run.id,
            kind=ArtifactKind.ACCEPTANCE_CRITERIA,
            content="This is an AC artifact",
        )
        session.add_all([artifact_1, artifact_2])

        await session.commit()
        run_id = stage_run.id
        session.expire_all()

        stored_artifacts = (
            await session.scalars(
                sa.select(Artifact).where(Artifact.stage_run_id == run_id)
            )
        ).all()

        assert len(stored_artifacts) == 2
        assert {(a.kind, a.content) for a in stored_artifacts} == {
            (ArtifactKind.PRD, "This is a PRD artifact"),
            (ArtifactKind.ACCEPTANCE_CRITERIA, "This is an AC artifact"),
        }

    async def test_artifacts_link_the_right_work_item(
        self, session: AsyncSession, work_item: WorkItem
    ) -> None:
        pass

    async def test_deleting_run_deletes_artifacts(
        self, session: AsyncSession, work_item: WorkItem
    ) -> None:
        pass
