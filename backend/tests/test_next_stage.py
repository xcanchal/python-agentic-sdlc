import pytest

from agentic_sdlc.domain.enums import Stage
from agentic_sdlc.domain.errors import StageAlreadyCompletedError
from agentic_sdlc.domain.stages import next_stage


class TestNextStage:
    @pytest.mark.parametrize(
        ("current", "expected"),
        [
            (Stage.RESEARCH, Stage.DEFINITION),
            (Stage.DEFINITION, Stage.DESIGN),
            (Stage.DESIGN, Stage.IMPLEMENTATION),
            (Stage.IMPLEMENTATION, Stage.VERIFICATION),
            (Stage.VERIFICATION, Stage.DONE),
        ],
    )
    def test_valid_transitions(self, current: Stage, expected: Stage) -> None:
        assert next_stage(current) is expected

    def test_already_completed_error(self) -> None:
        with pytest.raises(StageAlreadyCompletedError):
            next_stage(Stage.DONE)
