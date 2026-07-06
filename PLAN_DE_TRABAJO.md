# Plan de Trabajo — Plataforma Web Segura de Firma Digital y Validación Criptográfica (DevSecOps)

> Documento guía del proyecto final de **Ingeniería de Seguridad del Software**.
> Sirve para (A) cerrar las decisiones de arranque y (B) implementar el sistema de forma **gradual, commit por commit**.
> Mantén este archivo actualizado a medida que avances (marca los checkboxes).

---

## 0. Cómo usar este documento

1. Primero completa la **Sección 1 (Decisiones a definir)**. Nada de código hasta cerrar esto.
2. Sigue la **Sección 4 (Hoja de ruta por commits)** en orden. Cada commit es pequeño, atómico y verificable.
3. Usa la **Sección 6 (Checklist de entregables)** como control final antes de la entrega.

Leyenda: `[ ]` pendiente · `[~]` en progreso · `[x]` hecho.

---

## 1. Decisiones que DEBEMOS cerrar antes de empezar

Esto es lo que hay que dejar 100 % definido y escrito. Cada punto tiene una **recomendación** para que el proyecto sea realista en 8-10 semanas.

### 1.1 Equipo y roles
- [ ] Integrantes (2-3) y correos.
- [ ] Roles rotativos sugeridos:
  - **Backend/Cripto** (Python, firma, hash, cifrado, CA).
  - **Frontend/UX** (interfaz, formularios, consumo de API).
  - **DevSecOps/Infra** (Git, CI/CD, escaneos, entorno virtual, red).
- [ ] Quién es el "dueño del repo" (protege `main`, revisa PRs).

> Nota: aunque haya roles, **todos tocan todo** (lo exige la rúbrica).

### 1.2 Stack tecnológico (con recomendación)
| Capa | Opciones que pide la guía | **Recomendación** | Por qué |
|------|---------------------------|-------------------|---------|
| Frontend | HTML/CSS/JS **o** React | **HTML/CSS/JS + Bootstrap** (o React solo si el equipo ya lo domina) | Menos fricción, foco en cripto y seguridad |
| Backend | Python + Flask **o** FastAPI | **FastAPI** | Async, validación con Pydantic, docs Swagger automáticas, tests fáciles |
| Base de datos | PostgreSQL **o** SQLite | **PostgreSQL** en Ubuntu Server; **SQLite** para desarrollo local | PostgreSQL es más "real" para la defensa; SQLite acelera el arranque |
| ORM | — | **SQLAlchemy + Alembic** (migraciones) | Estándar, portable entre SQLite y Postgres |
| Cripto | SHA-256, AES, RSA | librería **`cryptography`** (+ `passlib[bcrypt]` para contraseñas) | Mantenida, segura, evita implementar primitivas a mano |
| Auth | login seguro + sesiones | **JWT (access token)** con contraseñas **bcrypt** | Encaja con API stateless; sesión = token con expiración |
| Contenedores | (opcional) | **Docker + docker-compose** | Facilita CI, escaneo Trivy y despliegue en Ubuntu Server |

- [ ] Confirmar cada fila.

### 1.3 Metodología ágil
- [ ] Elegir **Scrum simplificado** (sprints de 1 semana) o **Kanban**.
- [ ] Herramienta de tablero: **GitHub Projects** (recomendado, queda todo en el repo).
- [ ] Definir **Sprint = 1 semana** alineado a la Sección 4.
- [ ] Registrar evidencia ágil: capturas del tablero, mini actas de reunión semanal.

### 1.4 Control de versiones y convenciones
- [x] Repositorio: **GitHub** (ya inicializado).
- [x] Estrategia de ramas: **una sola rama `main`** (trabajo directo, commits atómicos y frecuentes).
- [x] **Convención de commits: Conventional Commits**
  - `feat:` nueva funcionalidad · `fix:` bug · `docs:` documentación
  - `test:` pruebas · `chore:` config/infra · `refactor:` · `ci:` pipeline · `security:` mitigaciones
  - Ejemplo: `feat(auth): login con JWT y hash bcrypt`

### 1.5 Modelo de datos (entidades mínimas)
Definir tablas y campos. Propuesta base:
- [ ] **users**: `id, username, email, password_hash, role, is_active, created_at`
- [ ] **certificates**: `id, user_id, serial, public_key, cert_pem, status(valid/revoked/expired), issued_at, expires_at`
- [ ] **documents**: `id, user_id, filename, storage_path, sha256, is_deleted, created_at`
- [ ] **signatures**: `id, document_id, user_id, signature_b64, cert_id, algorithm, created_at`
- [ ] **audit_logs**: `id, user_id, event_type, detail, ip, created_at`
- [ ] Confirmar borrado **lógico** (`is_deleted`/`is_active`) vs físico donde aplique.

### 1.6 Alcance de la criptografía y la CA
- [ ] **Hash**: SHA-256 para integridad de documentos + bcrypt para contraseñas.
- [ ] **Simétrica**: AES-256 (modo **GCM**, autenticado) para cifrar archivos.
- [ ] **Asimétrica**: RSA-2048 (o 3072) para firma y para envolver la clave AES.
- [ ] **Firma digital**: RSA-PSS + SHA-256 sobre el hash del documento.
- [ ] **Certificados**: X.509 vía `cryptography`, con expiración.
- [ ] **CA simulada**: un par de claves raíz que firma los certificados de usuario; validación = verificar cadena + estado (no revocado) + no expirado.
- [ ] Definir dónde se guardan las **claves privadas** (cifradas en disco / KeyStore simple) — **nunca en Git**.

### 1.7 Entorno virtualizado y red
- [ ] Hypervisor: **VirtualBox** (o VMware).
- [ ] VMs: **Kali Linux**, **Ubuntu Desktop**, **Ubuntu Server**, **Metasploitable 2**.
- [ ] Red interna/host-only. Definir **IPs fijas**, por ejemplo:
  - Ubuntu Server (backend + DB): `192.168.56.10`
  - Ubuntu Desktop (cliente): `192.168.56.11`
  - Kali (pentesting): `192.168.56.20`
  - Metasploitable2 (objetivo de riesgo): `192.168.56.30`
- [ ] Documentar puertos abiertos (ej. API `:8000`, Postgres `:5432` solo interno).

### 1.8 DevSecOps / CI-CD
- [ ] Plataforma CI: **GitHub Actions**.
- [ ] Pipeline mínimo por push/PR:
  - Lint (`ruff`/`flake8`) + formato.
  - Tests (`pytest`).
  - **Bandit** (análisis estático de seguridad Python).
  - **pip-audit** / **OWASP Dependency-Check** (dependencias).
  - **Trivy** (si hay Docker/imagenes).
- [ ] Escaneo de red manual desde Kali: **Nmap** (documentado, no en CI).
- [ ] Gestión de secretos: **variables de entorno / GitHub Secrets**, archivo `.env` **ignorado** por Git.

### 1.9 Definición de "Hecho" (Definition of Done)
Un incremento está **Done** cuando:
- [ ] Código en rama `feature/*` con PR aprobado y mergeado.
- [ ] Tiene al menos una prueba automática relacionada.
- [ ] Pasa el pipeline (lint + tests + Bandit) en verde.
- [ ] Documentado (README/endpoint/uso).

---

## 2. Arquitectura objetivo

```
┌────────────────────────── Red host-only 192.168.56.0/24 ──────────────────────────┐
│                                                                                    │
│  Ubuntu Desktop (cliente)        Ubuntu Server (backend)         Kali Linux        │
│  ┌───────────────────┐           ┌────────────────────────┐      ┌──────────────┐  │
│  │ Frontend (HTML/JS)│──HTTPS──▶ │ FastAPI  :8000         │      │ Nmap/OWASP   │  │
│  │  login, CRUD,     │           │  - Auth JWT            │◀────▶│ Bandit/Trivy │  │
│  │  firmar, verificar│           │  - Servicios cripto    │      │ pruebas pentest│ │
│  └───────────────────┘           │  - CA simulada         │      └──────────────┘  │
│                                   │  - Audit logs          │                        │
│                                   │        │               │      Metasploitable2   │
│                                   │  PostgreSQL :5432      │      (objetivo riesgo)  │
│                                   └────────────────────────┘                        │
└────────────────────────────────────────────────────────────────────────────────────┘
```

Estructura de carpetas propuesta (monorepo):
```
/backend        FastAPI, servicios cripto, CA, modelos, tests
/frontend       HTML/CSS/JS (o React)
/infra          docker-compose, scripts VM, configuración red
/docs           informe técnico, artículo, evidencias, diagramas
/.github/workflows   pipelines CI/CD
```

---

## 3. Módulos criptográficos (contrato funcional)

Cada uno debe tener su prueba de "verificación" exigida por la rúbrica:

| Módulo | Función | Prueba de aceptación |
|--------|---------|----------------------|
| Hash | `sha256(file) -> hex` | mismo archivo → mismo hash; alterado → distinto |
| Password | `hash_password`, `verify_password` (bcrypt) | login correcto/incorrecto |
| AES-GCM | `encrypt_file`, `decrypt_file` | descifrado devuelve original; tag inválido → error |
| RSA | `generate_keypair`, `sign`, `verify` | doc modificado → firma inválida |
| Firma digital | firmar hash con RSA-PSS | detecta alteración |
| Certificados X.509 | `issue`, `validate`, `revoke` | válido / expirado / revocado / alterado |
| CA simulada | firma y valida cadena | cert firmado por CA → confiable; ajeno → no |

---

## 4. Hoja de ruta por COMMITS (implementación gradual)

Cada línea = **un commit**. Respeta el orden. Los mensajes ya vienen en Conventional Commits.

> **Línea de tiempo real: ~3 semanas (idealmente terminar esta semana).**
> Los "sprints" ya **no son semanales**: son bloques de trabajo. Objetivo de ritmo:
> - **Semana 1:** Sprints 1-4 (base, entorno, CRUD, auth+hash).
> - **Semana 2:** Sprints 5-6 (cripto simétrica/asimétrica, firma, certificados, CA, DevSecOps).
> - **Semana 3:** Sprints 7-8 (pruebas, pentesting, estadística, despliegue, informe y artículo).

### Sprint 1 — Bloque A: Fundamentos y planificación
- [ ] `docs: agregar PLAN_DE_TRABAJO y definir decisiones de arranque`
- [ ] `chore: estructura de carpetas (backend, frontend, infra, docs)`
- [ ] `chore: .gitignore (venv, .env, __pycache__, claves .pem, db)`
- [ ] `docs: README con objetivo, stack y cómo ejecutar`
- [ ] `chore(backend): entorno Python (requirements.txt / pyproject) y venv`
- [ ] `chore: configurar GitHub Projects y ramas main/develop`

### Sprint 2 — Semana 2: Entorno virtual + esqueleto backend
- [ ] `docs(infra): guía de instalación de VMs (Kali, Ubuntu x2, Metasploitable2) e IPs`
- [ ] `feat(backend): app FastAPI mínima con endpoint /health`
- [ ] `feat(backend): conexión a base de datos con SQLAlchemy (SQLite dev)`
- [ ] `feat(backend): modelos User, Certificate, Document, Signature, AuditLog`
- [ ] `chore(backend): migraciones con Alembic`
- [ ] `test(backend): test de /health y de creación de tablas`
- [ ] `ci: workflow de GitHub Actions (lint + pytest)`

### Sprint 3 — Semana 3: CRUD + Frontend base
- [ ] `feat(backend): CRUD de usuarios (crear, listar, actualizar, eliminar lógico)`
- [ ] `feat(backend): CRUD de documentos (subir, listar, eliminar lógico)`
- [ ] `feat(frontend): layout base, login page y dashboard`
- [ ] `feat(frontend): formularios CRUD de usuarios y documentos consumiendo la API`
- [ ] `test(backend): tests de CRUD (happy path + validaciones)`
- [ ] `security: validación de entradas con Pydantic y manejo de errores`

### Sprint 4 — Semana 4: Autenticación + Hash
- [ ] `feat(auth): registro con contraseña hasheada (bcrypt)`
- [ ] `feat(auth): login con JWT y expiración de sesión`
- [ ] `feat(auth): middleware/dependency para proteger endpoints`
- [ ] `feat(crypto): servicio SHA-256 para integridad de documentos`
- [ ] `feat(backend): guardar sha256 al subir documento y endpoint de verificación`
- [ ] `test(crypto): mismo archivo→mismo hash, alterado→distinto`
- [ ] `feat(audit): registrar accesos y eventos de login en audit_logs`

### Sprint 5 — Semana 5: Criptografía simétrica y asimétrica
- [ ] `feat(crypto): cifrado/descifrado de archivos con AES-256-GCM`
- [ ] `feat(backend): endpoints cifrar/descifrar documento`
- [ ] `feat(crypto): generación de par de claves RSA por usuario`
- [ ] `feat(crypto): almacenamiento seguro de clave privada (cifrada, fuera de Git)`
- [ ] `test(crypto): AES round-trip y detección de tag inválido`
- [ ] `feat(frontend): UI para cifrar/descifrar y descargar archivos`

### Sprint 6 — Semana 6: Firma digital, certificados, CA y DevSecOps
- [ ] `feat(crypto): firma RSA-PSS + SHA-256 y verificación`
- [ ] `feat(backend): endpoints firmar documento y verificar firma`
- [ ] `feat(ca): autoridad certificadora simulada (clave raíz + firma de certs)`
- [ ] `feat(cert): emitir certificado X.509 con expiración`
- [ ] `feat(cert): validar (cadena + expiración) y revocar certificados`
- [ ] `feat(frontend): UI de firma, verificación y gestión de certificados`
- [ ] `ci: agregar Bandit y pip-audit al pipeline`
- [ ] `security: documentar y mitigar hallazgos de Bandit/dependencias`

### Sprint 7 — Semana 7: Pruebas, pentesting y análisis estadístico
- [ ] `test: suite de verificación (hash, firma, certificados válidos/expirados/alterados)`
- [ ] `docs(security): escaneo Nmap desde Kali y resultados`
- [ ] `docs(security): pruebas sobre Metasploitable2 y registro de vulnerabilidades`
- [ ] `docs(security): tabla de vulnerabilidades (severidad + mitigación)`
- [ ] `feat(stats): script que mide tiempos (cifrado, validación) y exporta CSV`
- [ ] `docs(stats): notebook/graficos (pandas + matplotlib) con métricas`
- [ ] `feat(monitoreo): endpoint/reporte básico de logs y auditoría`

### Sprint 8 — Semana 8: Despliegue, informe y defensa
- [ ] `feat(infra): docker-compose (backend + Postgres) para Ubuntu Server`
- [ ] `ci: escaneo Trivy de la imagen Docker`
- [ ] `docs: informe técnico completo`
- [ ] `docs: artículo técnico (estructura de 8 secciones)`
- [ ] `docs: guion y enlace del video demostrativo`
- [ ] `docs: presentación de defensa`
- [ ] `chore: release v1.0.0 y limpieza final`

---

## 5. Pipeline DevSecOps (resumen operativo)

En cada `push`/PR, GitHub Actions ejecuta:
1. **Lint/format** — `ruff` o `flake8`.
2. **Tests** — `pytest` (con cobertura).
3. **SAST** — `bandit -r backend`.
4. **Dependencias** — `pip-audit` (u OWASP Dependency-Check).
5. **Contenedor** (si aplica) — `trivy image`.

Manual desde Kali (documentar en `/docs/security`):
- `nmap` a Ubuntu Server y Metasploitable2.
- Pruebas de vulnerabilidades y su mitigación.

---

## 6. Checklist de entregables finales

- [ ] **Código fuente** en Git, documentado, pipeline en verde.
- [ ] **Plataforma funcionando** en el entorno virtualizado (Ubuntu Server).
- [ ] **Informe técnico**.
- [ ] **Artículo técnico** (8 secciones: Introducción, Marco teórico, Metodología, Implementación, Evaluación experimental, Verificación y validación, Resultados, Conclusiones).
- [ ] **Video demostrativo**.
- [ ] **Presentación y defensa**.
- [ ] Evidencias: capturas del tablero ágil, escaneos, gráficos estadísticos.

Ponderación: Implementación 50 % · Artículo 25 % · Defensa 25 %.

---

## 7. Primeros pasos concretos (para hoy)

1. Completar todos los checkbox de la **Sección 1** en reunión de equipo.
2. Confirmar el stack (recomendado: **FastAPI + PostgreSQL/SQLite + `cryptography` + JWT + HTML-JS/Bootstrap**).
3. Ejecutar los commits del **Sprint 1** en orden.
4. Crear el tablero en GitHub Projects con las tarjetas de la Sección 4.
