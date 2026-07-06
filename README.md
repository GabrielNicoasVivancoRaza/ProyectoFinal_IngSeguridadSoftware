# Plataforma Web Segura de Firma Digital y Validación Criptográfica (DevSecOps)

Proyecto final de **Ingeniería de Seguridad del Software** — 7mo semestre.

Plataforma web que permite autenticación segura, generación de claves, firma digital de
documentos, verificación de integridad con hash, cifrado/descifrado de archivos y emisión y
validación de certificados mediante una Autoridad Certificadora (CA) simulada, aplicando
prácticas **DevSecOps** en todo el ciclo de vida.

## Stack tecnológico

| Capa | Tecnología |
|------|------------|
| Frontend | HTML / CSS / JavaScript (Bootstrap) |
| Backend | Python + **FastAPI** |
| Base de datos | **PostgreSQL** (gestionado con pgAdmin4) |
| ORM / Migraciones | SQLAlchemy + Alembic |
| Criptografía | `cryptography`, `passlib[bcrypt]`, JWT |
| CI/CD | GitHub Actions (lint + tests + Bandit + pip-audit) |
| Entorno | VMs: Kali, Ubuntu Desktop, Ubuntu Server, Metasploitable2 |

> Estrategia de trabajo: una sola rama `main`, commits atómicos siguiendo Conventional Commits.
> Ver [PLAN_DE_TRABAJO.md](PLAN_DE_TRABAJO.md) para la hoja de ruta completa.

## Estructura del repositorio

```
/backend        API FastAPI, servicios criptográficos, CA, modelos y pruebas
/frontend       Interfaz web (HTML/CSS/JS)
/infra          docker-compose, scripts de VMs y configuración de red
/docs           Informe técnico, artículo y evidencias
/.github/workflows   Pipelines de CI/CD
```

## Puesta en marcha (backend)

Requisitos: Python 3.11+, PostgreSQL en ejecución.

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux:    source .venv/bin/activate
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env   # y ajustar DATABASE_URL / SECRET_KEY

# Crear las tablas en PostgreSQL (migraciones Alembic)
alembic upgrade head

# Ejecutar la API
uvicorn app.main:app --reload
```

> Para crear una nueva migración tras cambiar los modelos:
> `alembic revision --autogenerate -m "descripcion del cambio"` y luego `alembic upgrade head`.

- API: http://localhost:8000
- Documentación interactiva (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Pruebas

```bash
cd backend
pytest
```

## Análisis de seguridad (local)

```bash
cd backend
ruff check .        # estilo / lint
bandit -r app       # análisis estático de seguridad (SAST)
pip-audit           # vulnerabilidades en dependencias
```
