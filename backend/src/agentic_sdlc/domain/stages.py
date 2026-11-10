from agentic_sdlc.domain.enums import Stage
from agentic_sdlc.domain.errors import StageAlreadyCompletedError

STAGE_ORDER: tuple[Stage, ...] = (
    Stage.RESEARCH,
    Stage.DEFINITION,
    Stage.DESIGN,
    Stage.IMPLEMENTATION,
    Stage.VERIFICATION,
    Stage.DONE,
)


def next_stage(stage: Stage) -> Stage:
    if stage is Stage.DONE:
        raise StageAlreadyCompletedError

    return STAGE_ORDER[STAGE_ORDER.index(stage) + 1]
