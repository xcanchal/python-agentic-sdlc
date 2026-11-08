import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from agentic_sdlc.application.agents import RESEARCH_AGENT
from agentic_sdlc.application.costs import compute_cost_usd
from agentic_sdlc.application.model_runner import ModelRunner, ModelRunnerError
from agentic_sdlc.application.prompt_builder import build_prompt
from agentic_sdlc.application.work_items import get_work_item
from agentic_sdlc.domain.enums import ArtifactKind, Stage, StageRunStatus
from agentic_sdlc.infrastructure.database.models import Artifact, StageRun


async def run_stage(
    session: AsyncSession,
    *,
    work_item_id: uuid.UUID,
    runner: ModelRunner,
) -> StageRun:
    work_item = await get_work_item(session, work_item_id)

    stage_run = StageRun(
        work_item_id=work_item_id,
        stage=Stage.RESEARCH,
        model=RESEARCH_AGENT.model,
        status=StageRunStatus.RUNNING,
        artifacts=[],
    )

    session.add(stage_run)
    await session.commit()

    prompt = build_prompt(
        instructions=RESEARCH_AGENT.instructions,
        title=work_item.title,
        description=work_item.description,
    )

    try:
        model_result = await runner.run(model=stage_run.model, prompt=prompt)
    except ModelRunnerError as error:
        stage_run.status = StageRunStatus.FAILED
        stage_run.error = str(error)
    else:
        stage_run.status = StageRunStatus.COMPLETED
        stage_run.input_tokens = model_result.input_tokens
        stage_run.output_tokens = model_result.output_tokens
        stage_run.cost_usd = compute_cost_usd(
            model=stage_run.model,
            input_tokens=model_result.input_tokens,
            output_tokens=model_result.output_tokens,
        )

        stage_run.artifacts.append(
            Artifact(kind=ArtifactKind.RESEARCH_BRIEF, content=model_result.text)
        )

    stage_run.completed_at = datetime.now(UTC)
    await session.commit()
    return stage_run
