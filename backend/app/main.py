from fastapi import FastAPI
from app.registry import router as registry_router

app = FastAPI(title="RWAs Intelligence API", version="0.1.0", description="Canonical identity registry and read-only market intelligence services.")
app.include_router(registry_router)

@app.get("/healthz", tags=["operations"])
def healthcheck():
    return {"status": "ok", "service": "rwa-intelligence-api"}
