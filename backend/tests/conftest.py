from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from agentic_sdlc.config.settings import settings
from agentic_sdlc.domain.enums import Stage
from agentic_sdlc.infrastructure.database.models import (
    Base,
    Project,
    StageRun,
    WorkItem,
)
from agentic_sdlc.infrastructure.database.session import get_session
from agentic_sdlc.main import app

TEST_DATABASE_URL = make_url(settings.database_url).set(database="agentic_sdlc_test")


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=settings.database_echo)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def test_get_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = test_get_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def project(session: AsyncSession) -> Project:
    project = Project(name="Test Project")
    session.add(project)
    await session.commit()
    return project


@pytest.fixture
async def work_item(session: AsyncSession, project: Project) -> WorkItem:
    work_item = WorkItem(project_id=project.id, title="Test", description="Details")
    session.add(work_item)
    await session.commit()
    return work_item


@pytest.fixture
async def stage_run(session: AsyncSession, work_item: WorkItem) -> StageRun:
    run = StageRun(work_item_id=work_item.id, stage=Stage.RESEARCH, model="test-model")
    session.add(run)
    await session.commit()
    return run
