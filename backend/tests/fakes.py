from dataclasses import KW_ONLY, dataclass, field

from agentic_sdlc.application.model_runner import ModelResult


@dataclass
class FakeModelRunner:
    text: str = "# Research brief"
    _: KW_ONLY
    error: Exception | None = None
    input_tokens: int = 100
    output_tokens: int = 200
    calls: list[dict[str, str]] = field(default_factory=list)

    async def run(self, *, model: str, prompt: str) -> ModelResult:
        self.calls.append({"model": model, "prompt": prompt})

        if self.error is not None:
            raise self.error

        return ModelResult(
            text=self.text,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
        )
