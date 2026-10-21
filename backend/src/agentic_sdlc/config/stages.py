from dataclasses import dataclass

from agentic_sdlc.domain.enums import ArtifactKind, Stage


@dataclass(frozen=True)
class StageDefinition:
    stage: Stage
    agent: str
    required_inputs: tuple[ArtifactKind, ...]
    possible_outputs: tuple[ArtifactKind, ...]


RESEARCH = StageDefinition(
    stage=Stage.RESEARCH,
    agent="research",
    required_inputs=(),
    possible_outputs=(ArtifactKind.RESEARCH_BRIEF,),
)
