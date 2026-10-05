import uuid

from fastapi import APIRouter, status

from agentic_sdlc.api.dependencies import SessionDependency
from agentic_sdlc.api.schemas import WorkItemCreateRequest, WorkItemResponse
from agentic_sdlc.application import work_items

work_items_router = APIRouter(tags=["work-items"])


@work_items_router.get("/projects/{project_id}/work-items")
async def list_work_items(
    session: SessionDependency,
    project_id: uuid.UUID,
) -> list[WorkItemResponse]:
    all_work_items = await work_items.list_work_items(session, project_id=project_id)
    return [WorkItemResponse.model_validate(work_item) for work_item in all_work_items]


@work_items_router.post(
    "/projects/{project_id}/work-items", status_code=status.HTTP_201_CREATED
)
async def create_work_item(
    session: SessionDependency, project_id: uuid.UUID, body: WorkItemCreateRequest
) -> WorkItemResponse:
    work_item = await work_items.create_work_item(
        session, project_id=project_id, title=body.title, description=body.description
    )
    return WorkItemResponse.model_validate(work_item)


@work_items_router.get("/work-items/{work_item_id}")
async def get_work_item(
    session: SessionDependency, work_item_id: uuid.UUID
) -> WorkItemResponse:
    work_item = await work_items.get_work_item(session, work_item_id)
    return WorkItemResponse.model_validate(work_item)
