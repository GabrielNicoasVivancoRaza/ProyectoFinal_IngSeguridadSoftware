"""Configuracion central de la aplicacion cargada desde variables de entorno."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Valores de configuracion. Se leen del archivo .env o del entorno."""

    app_name: str = "Plataforma Segura de Firma Digital"
    environment: str = "development"
    debug: bool = True

    # Base de datos
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/firma_digital"

    # Almacenamiento de archivos subidos
    storage_dir: str = "storage"

    # Seguridad / JWT
    secret_key: str = "cambia-esta-clave"
    access_token_expire_minutes: int = 60
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
