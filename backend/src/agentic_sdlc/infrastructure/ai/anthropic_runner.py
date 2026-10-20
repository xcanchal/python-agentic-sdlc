from anthropic import AsyncAnthropic


class AnthropicModelRunner:
    def __init__(self, api_key: str | None = None) -> None:
        self.client = AsyncAnthropic(api_key=api_key)
