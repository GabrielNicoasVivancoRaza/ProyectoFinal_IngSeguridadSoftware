"""Punto de entrada de la API FastAPI."""
from fastapi import FastAPI

from app.api.routes import auth, documents, users
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Plataforma web segura de firma digital y validacion criptografica (DevSecOps).",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)


@app.get("/", tags=["general"])
def root() -> dict:
    """Mensaje de bienvenida de la API."""
    return {"app": settings.app_name, "version": "0.1.0", "docs": "/docs"}


@app.get("/health", tags=["general"])
def health() -> dict:
    """Endpoint de salud para monitoreo y CI/CD."""
    return {"status": "ok", "environment": settings.environment}
