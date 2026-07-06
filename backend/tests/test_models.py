"""Verifica que los modelos ORM definan correctamente sus tablas."""
from sqlalchemy import create_engine, inspect

import app.models  # noqa: F401  (registra todos los modelos en Base.metadata)
from app.db.session import Base


def test_metadata_crea_todas_las_tablas():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    tablas = set(inspect(engine).get_table_names())
    esperadas = {"users", "certificates", "documents", "signatures", "audit_logs"}
    assert esperadas.issubset(tablas)


def test_columnas_clave_de_usuario():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    columnas = {c["name"] for c in inspect(engine).get_columns("users")}
    assert {"id", "username", "email", "password_hash", "is_active"}.issubset(columnas)
