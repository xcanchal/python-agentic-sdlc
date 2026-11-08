from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_sdlc.application.model_runner import ModelRunner
from agentic_sdlc.config.settings import settings
from agentic_sdlc.infrastructure.ai.anthropic_runner import AnthropicModelRunner
from agentic_sdlc.infrastructure.database.session import get_session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]


def get_model_runner() -> ModelRunner:
    api_key = settings.anthropic_api_key
    return AnthropicModelRunner(api_key=api_key.get_secret_value() if api_key else None)


ModelRunnerDependency = Annotated[ModelRunner, Depends(get_model_runner)]
