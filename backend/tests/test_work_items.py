import uuid
from datetime import datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_sdlc.api.dependencies import get_model_runner
from agentic_sdlc.application.model_runner import ModelRunnerError
from agentic_sdlc.domain.enums import (
    ArtifactKind,
    Stage,
    StageRunStatus,
    WorkItemStatus,
)
from agentic_sdlc.domain.limits import (
    WORK_ITEM_DESCRIPTION_MAX_LENGTH,
    WORK_ITEM_TITLE_MAX_LENGTH,
)
from agentic_sdlc.infrastructure.database.models import Project, WorkItem
from agentic_sdlc.main import app
from tests.fakes import FakeModelRunner


async def add_work_item(
    session: AsyncSession, project: Project, title: str
) -> WorkItem:
    work_item = WorkItem(project_id=project.id, title=title, description="Details")
    session.add(work_item)
    await session.commit()
    return work_item


class TestCreateWorkItem:
    async def test_stores_the_work_item_in_research(
        self, session: AsyncSession, client: AsyncClient, project: Project
    ) -> None:
        response = await client.post(
            f"/projects/{project.id}/work-items",
            json={
                "title": "Add model routing",
                "description": "Route prompts by need.",
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["project_id"] == str(project.id)
        assert body["title"] == "Add model routing"
        assert body["description"] == "Route prompts by need."
        assert body["current_stage"] == "RESEARCH"
        assert body["status"] == "ACTIVE"

        # The app shares this session, so drop uncommitted state to read only what was persisted.
        await session.rollback()
        work_item = await session.get(WorkItem, uuid.UUID(body["id"]))
        assert work_item is not None
        assert work_item.current_stage is Stage.RESEARCH
        assert work_item.status is WorkItemStatus.ACTIVE
        assert datetime.fromisoformat(body["created_at"]) == work_item.created_at
        assert datetime.fromisoformat(body["updated_at"]) == work_item.updated_at
        assert work_item.updated_at == work_item.created_at

    async def test_returns_404_when_project_is_unknown(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            f"/projects/{uuid.uuid4()}/work-items",
            json={"title": "Title", "description": "Details"},
        )

        assert response.status_code == 404

    async def test_rejects_empty_title(
        self, client: AsyncClient, project: Project
    ) -> None:
        response = await client.post(
            f"/projects/{project.id}/work-items",
            json={"title": "", "description": "Details"},
        )

        assert response.status_code == 422

    async def test_rejects_title_over_max_length(
        self, client: AsyncClient, project: Project
    ) -> None:
        response = await client.post(
            f"/projects/{project.id}/work-items",
            json={
                "title": "x" * (WORK_ITEM_TITLE_MAX_LENGTH + 1),
                "description": "Details",
            },
        )

        assert response.status_code == 422

    async def test_rejects_empty_description(
        self, client: AsyncClient, project: Project
    ) -> None:
        response = await client.post(
            f"/projects/{project.id}/work-items",
            json={"title": "Title", "description": ""},
        )

        assert response.status_code == 422

    async def test_rejects_description_over_max_length(
        self, client: AsyncClient, project: Project
    ) -> None:
        response = await client.post(
            f"/projects/{project.id}/work-items",
            json={
                "title": "Title",
                "description": "x" * (WORK_ITEM_DESCRIPTION_MAX_LENGTH + 1),
            },
        )

        assert response.status_code == 422

    async def test_ignores_client_supplied_stage_and_status(
        self, client: AsyncClient, project: Project
    ) -> None:
        response = await client.post(
            f"/projects/{project.id}/work-items",
            json={
                "title": "Title",
                "description": "Details",
                "current_stage": "DONE",
                "status": "DONE",
            },
        )

        assert response.status_code == 201
        assert response.json()["current_stage"] == "RESEARCH"
        assert response.json()["status"] == "ACTIVE"


class TestListWorkItems:
    async def test_returns_empty_list(
        self, client: AsyncClient, project: Project
    ) -> None:
        response = await client.get(f"/projects/{project.id}/work-items")

        assert response.status_code == 200
        assert response.json() == []

    async def test_returns_only_this_projects_items_newest_first(
        self, session: AsyncSession, client: AsyncClient, project: Project
    ) -> None:
        other_project = Project(name="Other")
        session.add(other_project)
        await session.commit()
        first = await add_work_item(session, project, "First")
        await add_work_item(session, other_project, "Other project item")
        second = await add_work_item(session, project, "Second")
        assert second.created_at > first.created_at

        response = await client.get(f"/projects/{project.id}/work-items")

        assert response.status_code == 200
        assert [(w["id"], w["title"]) for w in response.json()] == [
            (str(second.id), "Second"),
            (str(first.id), "First"),
        ]

    async def test_returns_404_when_project_is_unknown(
        self, client: AsyncClient
    ) -> None:
        response = await client.get(f"/projects/{uuid.uuid4()}/work-items")

        assert response.status_code == 404


class TestGetWorkItem:
    async def test_returns_the_work_item(
        self, session: AsyncSession, client: AsyncClient, project: Project
    ) -> None:
        work_item = await add_work_item(session, project, "Title")

        response = await client.get(f"/work-items/{work_item.id}")

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == str(work_item.id)
        assert body["project_id"] == str(project.id)
        assert body["title"] == "Title"
        assert body["description"] == "Details"
        assert body["current_stage"] == "RESEARCH"
        assert body["status"] == "ACTIVE"
        assert datetime.fromisoformat(body["created_at"]) == work_item.created_at
        assert datetime.fromisoformat(body["updated_at"]) == work_item.updated_at

    async def test_returns_404_when_unknown(self, client: AsyncClient) -> None:
        response = await client.get(f"/work-items/{uuid.uuid4()}")

        assert response.status_code == 404

    async def test_rejects_invalid_uuid(self, client: AsyncClient) -> None:
        response = await client.get("/work-items/not-a-uuid")

        assert response.status_code == 422


class TestRunWorkItem:
    async def test_returns_the_completed_run_with_its_artifact(
        self, client: AsyncClient, work_item: WorkItem
    ) -> None:
        app.dependency_overrides[get_model_runner] = lambda: FakeModelRunner()

        response = await client.post(f"/work-items/{work_item.id}/run")

        assert response.status_code == 201
        body = response.json()
        assert body["work_item_id"] == str(work_item.id)
        assert body["stage"] == Stage.RESEARCH
        assert body["status"] == StageRunStatus.COMPLETED
        assert body["error"] is None
        assert body["cost_usd"] == "0.0022"
        assert [(a["kind"], a["content"]) for a in body["artifacts"]] == [
            (ArtifactKind.RESEARCH_BRIEF, "# Research brief")
        ]
        assert body["artifacts"][0]["stage_run_id"] == body["id"]

    async def test_returns_the_failed_run_when_provider_fails(
        self, client: AsyncClient, work_item: WorkItem
    ) -> None:
        app.dependency_overrides[get_model_runner] = lambda: FakeModelRunner(
            error=ModelRunnerError("boom")
        )

        response = await client.post(f"/work-items/{work_item.id}/run")

        assert response.status_code == 201
        body = response.json()
        assert body["status"] == StageRunStatus.FAILED
        assert body["error"] == "boom"
        assert body["artifacts"] == []

    async def test_returns_404_when_unknown(self, client: AsyncClient) -> None:
        app.dependency_overrides[get_model_runner] = lambda: FakeModelRunner()

        response = await client.post(f"/work-items/{uuid.uuid4()}/run")

        assert response.status_code == 404
