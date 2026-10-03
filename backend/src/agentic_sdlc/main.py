from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from agentic_sdlc.api.routes.projects import projects_router
from agentic_sdlc.application.errors import NotFoundError

app = FastAPI(title="Agentic SDLC")

app.include_router(projects_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(NotFoundError)
async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
