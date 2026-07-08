"""Configuracion comun de pruebas: cliente de FastAPI con BD SQLite en memoria."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (registra los modelos en Base.metadata)
from app.core.config import settings
from app.db.session import Base, get_db
from app.main import app


@pytest.fixture
def client(tmp_path):
    # Redirige el almacenamiento de archivos a un directorio temporal por prueba.
    settings.storage_dir = str(tmp_path / "storage")

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Registra un usuario, inicia sesion y devuelve los headers con el token JWT."""
    client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "supersegura1"},
    )
    token = client.post(
        "/auth/login",
        data={"username": "bob", "password": "supersegura1"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
