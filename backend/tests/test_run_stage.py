import uuid
from decimal import Decimal

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_sdlc.application.agents import RESEARCH_AGENT
from agentic_sdlc.application.errors import NotFoundError
from agentic_sdlc.application.model_runner import ModelRunnerError
from agentic_sdlc.application.run_stage import run_stage
from agentic_sdlc.domain.enums import ArtifactKind, Stage, StageRunStatus
from agentic_sdlc.infrastructure.database.models import Artifact, StageRun, WorkItem
from tests.fakes import FakeModelRunner


class TestRunStage:
    async def test_run_completes_successfully(
        self, session: AsyncSession, work_item: WorkItem
    ) -> None:
        model_runner = FakeModelRunner()

        stage_run = await run_stage(
            session=session, work_item_id=work_item.id, runner=model_runner
        )

        assert work_item.title in model_runner.calls[0]["prompt"]

        run_id = stage_run.id
        work_item_id = work_item.id
        session.expire_all()
        stored = await session.get(StageRun, run_id)

        assert stored is not None

        assert stored.stage == Stage.RESEARCH
        assert stored.status == StageRunStatus.COMPLETED
        assert stored.error is None
        assert stored.work_item_id == work_item_id
        assert stored.input_tokens == 100
        assert stored.output_tokens == 200
        assert stored.model == RESEARCH_AGENT.model
        assert stored.created_at is not None
        assert stored.completed_at is not None
        assert stored.cost_usd == Decimal("0.0022")

        artifacts = (
            await session.scalars(
                sa.select(Artifact).where(Artifact.stage_run_id == stored.id)
            )
        ).all()

        assert [(a.kind, a.content) for a in artifacts] == [
            (ArtifactKind.RESEARCH_BRIEF, "# Research brief")
        ]

    async def test_run_fails_when_provider_fails(
        self, session: AsyncSession, work_item: WorkItem
    ) -> None:
        model_runner = FakeModelRunner(error=ModelRunnerError("Provider is down"))

        stage_run = await run_stage(
            session=session, work_item_id=work_item.id, runner=model_runner
        )

        assert stage_run.status == StageRunStatus.FAILED
        assert stage_run.error == "Provider is down"
        assert stage_run.completed_at is not None
        assert stage_run.input_tokens is None
        assert stage_run.output_tokens is None
        assert stage_run.cost_usd is None

        artifacts = (
            await session.scalars(
                sa.select(Artifact).where(Artifact.stage_run_id == stage_run.id)
            )
        ).all()

        assert artifacts == []

    async def test_unknown_work_item_raises(self, session: AsyncSession) -> None:
        with pytest.raises(NotFoundError):
            await run_stage(
                session=session, work_item_id=uuid.uuid4(), runner=FakeModelRunner()
            )

        runs = (await session.scalars(sa.select(StageRun))).all()
        assert runs == []
