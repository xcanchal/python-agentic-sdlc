from fastapi import FastAPI

app = FastAPI(title="Agentic SDLC")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
