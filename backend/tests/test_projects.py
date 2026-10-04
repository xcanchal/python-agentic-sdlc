import uuid
from datetime import datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_sdlc.domain.limits import PROJECT_NAME_MAX_LENGTH
from agentic_sdlc.infrastructure.database.models import Project


class TestListProjects:
    async def test_returns_empty_list(self, client: AsyncClient) -> None:
        response = await client.get("/projects")

        assert response.status_code == 200
        assert response.json() == []

    async def test_returns_newest_first(
        self, session: AsyncSession, client: AsyncClient
    ) -> None:
        first = Project(name="First")
        session.add(first)
        await session.commit()
        second = Project(name="Second")
        session.add(second)
        await session.commit()
        assert second.created_at > first.created_at

        response = await client.get("/projects")

        assert response.status_code == 200
        projects = response.json()
        assert [(p["id"], p["name"]) for p in projects] == [
            (str(second.id), "Second"),
            (str(first.id), "First"),
        ]
        assert [datetime.fromisoformat(p["created_at"]) for p in projects] == [
            second.created_at,
            first.created_at,
        ]


class TestCreateProject:
    async def test_stores_the_project(
        self, session: AsyncSession, client: AsyncClient
    ) -> None:
        response = await client.post("/projects", json={"name": "Test Project"})

        assert response.status_code == 201
        project = response.json()
        assert project["name"] == "Test Project"

        # The app shares this session, so drop uncommitted state to read only what was persisted.
        await session.rollback()
        project = await session.get(Project, uuid.UUID(project["id"]))
        assert project is not None
        assert project.name == "Test Project"

    async def test_accepts_name_at_max_length(self, client: AsyncClient) -> None:
        name = "x" * PROJECT_NAME_MAX_LENGTH

        response = await client.post("/projects", json={"name": name})

        assert response.status_code == 201
        assert response.json()["name"] == name

    async def test_rejects_empty_name(self, client: AsyncClient) -> None:
        response = await client.post("/projects", json={"name": ""})

        assert response.status_code == 422

    async def test_rejects_name_over_max_length(self, client: AsyncClient) -> None:
        response = await client.post(
            "/projects", json={"name": "x" * (PROJECT_NAME_MAX_LENGTH + 1)}
        )

        assert response.status_code == 422

    async def test_rejects_missing_name(self, client: AsyncClient) -> None:
        response = await client.post("/projects", json={})

        assert response.status_code == 422

    async def test_rejects_malformed_json(self, client: AsyncClient) -> None:
        response = await client.post(
            "/projects",
            content="{not json",
            headers={"content-type": "application/json"},
        )

        assert response.status_code == 422


class TestGetProject:
    async def test_returns_the_project(
        self, session: AsyncSession, client: AsyncClient
    ) -> None:
        project = Project(name="Test Project")
        session.add(project)
        await session.commit()

        response = await client.get(f"/projects/{project.id}")

        assert response.status_code == 200
        project_json = response.json()
        assert project_json["id"] == str(project.id)
        assert project_json["name"] == "Test Project"
        assert datetime.fromisoformat(project_json["created_at"]) == project.created_at

    async def test_returns_404_when_unknown(self, client: AsyncClient) -> None:
        response = await client.get(f"/projects/{uuid.uuid4()}")

        assert response.status_code == 404

    async def test_rejects_invalid_uuid(self, client: AsyncClient) -> None:
        response = await client.get("/projects/not-a-uuid")

        assert response.status_code == 422
