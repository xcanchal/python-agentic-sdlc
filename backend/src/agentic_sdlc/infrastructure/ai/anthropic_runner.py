import anthropic

from agentic_sdlc.application.model_runner import ModelResult, ModelRunnerError

MAX_TOKENS = 16000


class AnthropicModelRunner:
    def __init__(self, api_key: str | None = None) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def run(self, *, model: str, prompt: str) -> ModelResult:
        try:
            message = await self.client.messages.create(
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
                model=model,
            )

            if message.stop_reason == "refusal":
                raise ModelRunnerError("Model refused the request")

            if message.stop_reason == "max_tokens":
                raise ModelRunnerError("Response reached max_tokens")

            text = "".join(
                block.text for block in message.content if block.type == "text"
            )

            return ModelResult(
                text=text,
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
            )

        except anthropic.APIError as error:
            raise ModelRunnerError(str(error)) from error
