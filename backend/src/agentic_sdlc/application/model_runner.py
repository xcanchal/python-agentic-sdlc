from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModelResult:
    text: str
    input_tokens: int
    output_tokens: int


class ModelRunner(Protocol):
    async def run(
        self,
        *,
        model: str,
        prompt: str,
    ) -> ModelResult: ...


class ModelRunnerError(Exception):
    """Exception raised when a model provider call fails"""
