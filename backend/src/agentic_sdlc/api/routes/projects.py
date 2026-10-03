import uuid

from fastapi import APIRouter, status

from agentic_sdlc.api.dependencies import SessionDependency
from agentic_sdlc.api.schemas import ProjectCreateRequest, ProjectResponse
from agentic_sdlc.application import projects

projects_router = APIRouter(prefix="/projects", tags=["projects"])


@projects_router.get("")
async def list_projects(
    session: SessionDependency,
) -> list[ProjectResponse]:
    all_projects = await projects.list_projects(session)
    return [ProjectResponse.model_validate(project) for project in all_projects]


@projects_router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreateRequest,
    session: SessionDependency,
) -> ProjectResponse:
    project = await projects.create_project(session, body.name)
    return ProjectResponse.model_validate(project)


@projects_router.get("/{project_id}")
async def get_project(
    project_id: uuid.UUID,
    session: SessionDependency,
) -> ProjectResponse:
    project = await projects.get_project(session, project_id)
    return ProjectResponse.model_validate(project)
