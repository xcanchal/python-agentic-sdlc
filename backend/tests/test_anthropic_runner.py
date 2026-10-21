import anthropic
import httpx2
import pytest
from anthropic.types import Message, TextBlock, ThinkingBlock, Usage
from pytest import MonkeyPatch

from agentic_sdlc.infrastructure.ai.anthropic_runner import (
    AnthropicModelRunner,
    ModelRunnerError,
)


@pytest.fixture
def runner() -> AnthropicModelRunner:
    return AnthropicModelRunner(api_key="test")


def make_message(stop_reason: str = "end_turn") -> Message:
    return Message.model_construct(
        stop_reason=stop_reason,
        content=[
            TextBlock(type="text", text="foo"),
            ThinkingBlock(type="thinking", thinking="...", signature="sig"),
            TextBlock(type="text", text="bar"),
        ],
        usage=Usage(input_tokens=3, output_tokens=5),
    )


async def fake_messages_create(**kwargs: object) -> Message:
    return make_message()


async def fake_messages_create_refusal_model(**kwargs: object) -> Message:
    return make_message("refusal")


async def fake_messages_create_max_tokens(**kwargs: object) -> Message:
    return make_message("max_tokens")


async def fake_messages_create_api_error(**_: object) -> Message:
    raise anthropic.APIConnectionError(
        request=httpx2.Request("POST", "https://api.anthropic.com")
    )


""" @pytest.fixture
def stub_create(monkeypatch: MonkeyPatch, runner: AnthropicModelRunner):
    def stub(message: Message) -> None:
        async def create(**_: object) -> Message:
            return message
        monkeypatch.setattr(runner.client.messages, "create", create)
    return stub """


class TestAnthropicModelRunner:
    async def test_anthropic_runner_joins_text_blocks(
        self, monkeypatch: MonkeyPatch, runner: AnthropicModelRunner
    ) -> None:
        monkeypatch.setattr(runner.client.messages, "create", fake_messages_create)
        result = await runner.run(model="test", prompt="prompt")
        assert result.text == "foobar"
        assert result.input_tokens == 3
        assert result.output_tokens == 5

    async def test_anthropic_runner_refuses_model(
        self, monkeypatch: MonkeyPatch, runner: AnthropicModelRunner
    ) -> None:
        monkeypatch.setattr(
            runner.client.messages, "create", fake_messages_create_refusal_model
        )

        with pytest.raises(ModelRunnerError, match="Model refused the request"):
            await runner.run(model="test", prompt="prompt")

    async def test_anthropic_runner_refuses_max_tokens(
        self, monkeypatch: MonkeyPatch, runner: AnthropicModelRunner
    ) -> None:
        monkeypatch.setattr(
            runner.client.messages, "create", fake_messages_create_max_tokens
        )

        with pytest.raises(ModelRunnerError, match="Response reached max_tokens"):
            await runner.run(model="test", prompt="prompt")

    async def test_anthropic_runner_api_fails(
        self, monkeypatch: MonkeyPatch, runner: AnthropicModelRunner
    ) -> None:
        monkeypatch.setattr(
            runner.client.messages, "create", fake_messages_create_api_error
        )

        with pytest.raises(ModelRunnerError) as exc_info:
            await runner.run(model="test", prompt="prompt")
        assert isinstance(exc_info.value.__cause__, anthropic.APIConnectionError)
