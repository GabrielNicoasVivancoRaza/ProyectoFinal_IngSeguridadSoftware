# Gestión de Vulnerabilidades

Registro de riesgos identificados, su severidad y las mitigaciones aplicadas.
Combina (A) controles de seguridad **ya implementados** en la plataforma y
(B) hallazgos de las herramientas DevSecOps.

Severidad: 🔴 Alta · 🟠 Media · 🟡 Baja · ✅ Mitigado

---

## A. Controles de seguridad implementados (verificables en el código y las pruebas)

| # | Riesgo | Sev. | Mitigación implementada | Evidencia |
|---|--------|------|-------------------------|-----------|
| A1 | Contraseñas en texto plano | 🔴 | Hash **bcrypt** con salt por usuario | `app/core/security.py`; test que verifica que el hash no se expone |
| A2 | Acceso no autorizado a recursos | 🔴 | **JWT** obligatorio en documentos, certificados y auditoría | `app/api/deps.py`; tests devuelven `401` sin token |
| A3 | Manipulación de documentos | 🟠 | **SHA-256** de integridad + **firma RSA-PSS** | `test_documents`, `test_crypto_asymmetric` |
| A4 | Lectura/alteración de archivos cifrados | 🟠 | **AES-256-GCM** (cifrado autenticado): detecta manipulación | `test_crypto_symmetric` (tag inválido → falla) |
| A5 | Certificados falsos o caducados aceptados | 🟠 | Validación de **firma de la CA + expiración + revocación** | `test_certificates` |
| A6 | Inyección / datos malformados | 🟠 | Validación de entrada con **Pydantic** en todos los endpoints | Schemas `app/schemas/*` |
| A7 | Path traversal al subir archivos | 🟡 | `os.path.basename` + nombre aleatorio (UUID) | `app/services/storage.py` |
| A8 | Secretos en el repositorio | 🔴 | `.env`, `*.pem`, `ca_data/` en `.gitignore`; secretos por variables de entorno | `.gitignore`, `docker-compose.yml` |
| A9 | Contenedor con privilegios de root | 🟡 | Imagen Docker corre como **usuario sin privilegios** | `backend/Dockerfile` (`USER appuser`) |
| A10 | Repudio de acciones (sin trazabilidad) | 🟡 | **Auditoría** de accesos y eventos criptográficos con IP | `app/services/audit.py` |

---

## B. Análisis con herramientas DevSecOps

### B1. Bandit (análisis estático — SAST)
```bash
cd backend && bandit -r app -ll
```
**Resultado actual:** `No issues identified` (0 hallazgos de severidad media/alta).

**Resultado real (pegar cuando lo ejecutes):**
```
<pegar salida>
```

### B2. pip-audit (dependencias)
```bash
cd backend && pip-audit
```
**Resultado (pegar salida real):**
```
<pegar salida — registrar CVEs de dependencias, si aparecen>
```

### B3. Trivy (imagen del contenedor)
```bash
docker build -t firma-backend ./backend
trivy image --severity HIGH,CRITICAL firma-backend
```
**Resultado (pegar salida real):**
```
<pegar salida>
```

### B4. Nmap (escaneo de red — ver pruebas-seguridad.md)
Superficie de ataque mínima en el backend (un solo puerto). Ver [pruebas-seguridad.md](pruebas-seguridad.md).

---

## C. Plantilla para registrar nuevos hallazgos

| # | Vulnerabilidad | Herramienta | Severidad | CVE (si aplica) | Estado | Mitigación |
|---|----------------|-------------|-----------|-----------------|--------|------------|
| C1 | | | | | Abierto/Mitigado | |

---

## D. Métricas de gestión (para el artículo)

Al cerrar las pruebas, completar:

- Vulnerabilidades detectadas: **___**
- Vulnerabilidades mitigadas: **___**
- Porcentaje mitigado: **___ %**
- Hallazgos de Bandit (SAST): **0** (estado actual)
- Superficie de ataque del backend: **1 puerto** (8000/API)

> Nota: las tasas de detección de alteraciones (100 %) y autenticación (100 %) se
> documentan en el [análisis estadístico](../../analysis/README.md).
