# Desarrollo de una Plataforma Web Segura de Firma Digital y Validación Criptográfica Aplicando DevSecOps

**Autores:** [COMPLETAR nombres de los integrantes]
**Carrera:** Ingeniería de Software — Ingeniería de Seguridad del Software
**Fecha:** [COMPLETAR]

---

## Resumen

Este trabajo presenta el diseño, implementación y evaluación de una plataforma web
segura para la firma digital y validación criptográfica de documentos, desarrollada
bajo principios de Ingeniería de Software, Criptografía Aplicada y DevSecOps. La
solución integra autenticación con tokens JWT, hashing de contraseñas con bcrypt,
verificación de integridad con SHA-256, cifrado simétrico AES-256-GCM, firma digital
RSA-PSS y una Autoridad Certificadora (CA) simulada que emite y valida certificados
X.509. El sistema se construyó con una arquitectura cliente-servidor (frontend
HTML/JS, backend FastAPI, base de datos PostgreSQL) e incorpora un pipeline de
integración continua con pruebas automáticas y análisis de seguridad (Bandit,
pip-audit, Trivy). La evaluación experimental, sobre 260 mediciones, demostró una
tasa de detección de alteraciones del 100 % en los tres mecanismos criptográficos y
una tasa de autenticación correcta del 100 %.

**Palabras clave:** criptografía aplicada, firma digital, certificados X.509,
DevSecOps, AES, RSA, integridad, FastAPI.

---

## 1. Introducción

La transformación digital ha desplazado hacia medios electrónicos procesos que
tradicionalmente dependían de documentos firmados en papel. Esto plantea un problema
central: **¿cómo garantizar la autenticidad, integridad y confidencialidad de un
documento digital?** Un archivo puede ser copiado, alterado o suplantado sin dejar
rastro visible, y sin mecanismos criptográficos adecuados no es posible probar quién
lo firmó ni si fue modificado.

La importancia de la seguridad en este contexto es crítica: sectores como el
financiero, legal y gubernamental requieren garantías verificables de que un
documento no ha sido manipulado y de que proviene de quien dice provenir. La
criptografía aplicada —funciones hash, cifrado simétrico y asimétrico, firmas
digitales y certificados— provee las herramientas para lograrlo.

Este proyecto aborda el problema mediante una plataforma web que integra estos
mecanismos en un flujo completo y usable, aplicando además prácticas **DevSecOps**
que incorporan la seguridad en todo el ciclo de vida del software, y no como una
etapa posterior.

### Objetivo

Desarrollar una plataforma web segura capaz de generar, firmar, validar y proteger
documentos digitales mediante criptografía aplicada y una CA simulada, en un entorno
virtualizado controlado, aplicando DevSecOps.

---

## 2. Marco Teórico

### 2.1 Funciones hash
Una función hash criptográfica transforma una entrada de tamaño arbitrario en una
salida de longitud fija (resumen), de forma unidireccional y resistente a colisiones.
Se usa **SHA-256** para verificar integridad: cualquier cambio en el documento produce
un resumen completamente distinto. Para contraseñas se emplea **bcrypt**, un algoritmo
de hashing deliberadamente lento con salt incorporado, que dificulta los ataques de
fuerza bruta.

### 2.2 Criptografía simétrica
Utiliza una misma clave para cifrar y descifrar. Se implementa **AES-256** en modo
**GCM** (Galois/Counter Mode), que además de confidencialidad ofrece **autenticación**:
si el dato cifrado o la clave son incorrectos, el descifrado falla. La clave se deriva
de una contraseña mediante **PBKDF2-HMAC-SHA256**.

### 2.3 Criptografía asimétrica
Emplea un par de claves: una **privada** (secreta) y una **pública** (compartible). Lo
cifrado/firmado con una se verifica con la otra. Se usa **RSA-2048**, base de la firma
digital y del intercambio seguro de claves.

### 2.4 Firma digital
Combina hash y criptografía asimétrica: se firma el resumen del documento con la clave
privada del emisor. Cualquiera con la clave pública puede verificar la firma; si el
documento fue alterado, la verificación falla. Se usa el esquema **RSA-PSS con SHA-256**.

### 2.5 Certificados digitales y Autoridad Certificadora
Un certificado **X.509** vincula una clave pública a una identidad y está firmado por
una **Autoridad Certificadora (CA)** de confianza. La validación comprueba la firma de
la CA (cadena de confianza), la vigencia (expiración) y el estado (revocación). En este
proyecto se implementa una **CA simulada** con su propia clave raíz autofirmada.

### 2.6 DevSecOps
Filosofía que integra seguridad (Sec) en el flujo de desarrollo (Dev) y operaciones
(Ops), automatizando controles: análisis estático (SAST), escaneo de dependencias y de
contenedores, y pruebas dentro de la integración continua (CI/CD).

### 2.7 Metodologías ágiles
El desarrollo iterativo e incremental permite entregar valor de forma continua. En este
proyecto se trabajó con incrementos pequeños y verificables, control de versiones con
Git y convención de commits (Conventional Commits).

---

## 3. Metodología

### 3.1 Arquitectura del sistema
Arquitectura **cliente-servidor** en capas:

- **Frontend** (cliente): HTML/CSS/JavaScript, consume la API vía HTTP.
- **Backend** (servidor): API REST con **FastAPI**, organizada en capas
  (routers → servicios/CRUD → modelos), con los servicios criptográficos aislados en
  el paquete `app/crypto`.
- **Base de datos**: **PostgreSQL**, gestionada con SQLAlchemy y migraciones Alembic.

Entidades principales: `users`, `documents`, `certificates`, `signatures`, `audit_logs`.

### 3.2 Entorno virtualizado
Red controlada (host-only) con cuatro máquinas virtuales:

| VM | Rol |
|----|-----|
| Ubuntu Server | Backend + PostgreSQL + APIs criptográficas |
| Ubuntu Desktop | Cliente legítimo |
| Kali Linux | Pentesting y escaneo |
| Metasploitable 2 | Objetivo vulnerable de referencia |

Detalle en [infra/entorno-virtualizado.md](infra/entorno-virtualizado.md).

### 3.3 Herramientas utilizadas

| Categoría | Herramienta |
|-----------|-------------|
| Backend | Python 3.11, FastAPI, SQLAlchemy, Alembic |
| Criptografía | `cryptography`, `passlib[bcrypt]`, `python-jose` |
| Base de datos | PostgreSQL, pgAdmin4 |
| Frontend | HTML, CSS, JavaScript |
| CI/CD | GitHub Actions |
| Seguridad | Bandit (SAST), pip-audit, Trivy, Nmap |
| Contenedores | Docker, docker-compose |
| Análisis | pandas, matplotlib |

### 3.4 Metodología ágil aplicada
Desarrollo incremental en bloques de trabajo, cada funcionalidad como un commit atómico
verificado (lint + pruebas + análisis de seguridad en verde) antes de integrarse. Control
de versiones en Git sobre una única rama estable.

---

## 4. Implementación

### 4.1 Backend y CRUD
La API expone operaciones CRUD para las tres entidades exigidas:

- **Usuarios**: crear, consultar, actualizar, eliminar (borrado lógico vía `is_active`).
- **Certificados**: emitir, consultar, validar, revocar.
- **Documentos**: subir, consultar, verificar integridad, eliminar (borrado lógico).

La validación de entradas se realiza con **Pydantic**; los errores devuelven códigos
HTTP apropiados (401, 404, 409, 400).

### 4.2 Base de datos
Modelo relacional con SQLAlchemy y migraciones versionadas con Alembic. Las relaciones
vinculan usuarios con sus documentos y certificados, y los documentos con sus firmas.

### 4.3 Integración criptográfica
Cada mecanismo se implementó como un servicio independiente y probado:

| Módulo | Función | Endpoint |
|--------|---------|----------|
| `hashing` | SHA-256 de documentos | `/documents/{id}/verify` |
| `security` | bcrypt + JWT | `/auth/login`, `/auth/register` |
| `symmetric` | AES-256-GCM | `/crypto/encrypt`, `/crypto/decrypt` |
| `asymmetric` | RSA-2048 + firma RSA-PSS | `/crypto/keys/generate`, `/sign`, `/verify` |
| `ca` | CA simulada + X.509 | `/certificates`, `/{id}/validate`, `/{id}/revoke` |

### 4.4 Autenticación y control de sesiones
Registro con contraseña hasheada (bcrypt) y login que emite un **JWT** con expiración.
Los endpoints sensibles exigen el token en el encabezado `Authorization`. Todos los
accesos y eventos criptográficos quedan registrados en la auditoría con su IP de origen.

### 4.5 Frontend
Interfaz web con login/registro y un panel con módulos para documentos, cifrado AES,
firma RSA, certificados y visualización del registro de auditoría.

### 4.6 DevSecOps
Pipeline de GitHub Actions que en cada commit ejecuta: lint (ruff), pruebas (pytest),
análisis estático (Bandit), auditoría de dependencias (pip-audit) y escaneo de la imagen
Docker (Trivy). Los secretos se gestionan por variables de entorno y nunca se versionan.

---

## 5. Evaluación Experimental

Se ejecutó un benchmark automatizado (`analysis/benchmark.py`) que mide los módulos
reales del backend, con **260 mediciones** en total, sobre archivos de 10 KB, 100 KB y
1 MB.

### 5.1 Métricas evaluadas
- Tiempo promedio de hash, cifrado/descifrado, firma/verificación (por tamaño).
- Tiempo de generación de claves, emisión y validación de certificados, y hashing de
  contraseñas.
- Tasa de detección de alteraciones (hash, firma, AES-GCM).
- Tasa de autenticación (credenciales correctas e incorrectas).

### 5.2 Suite de pruebas automáticas
El backend cuenta con **43 pruebas automáticas** que se ejecutan en el pipeline y
validan tanto la lógica CRUD como las propiedades criptográficas.

---

## 6. Verificación y Validación

### 6.1 Verificación de integridad (hash)
- Mismo archivo → mismo hash. ✔️
- Archivo alterado → hash diferente → integridad inválida. ✔️

### 6.2 Verificación de firma
- Documento intacto → firma válida. ✔️
- Documento modificado → firma inválida. ✔️
- Firma con clave distinta → inválida. ✔️

### 6.3 Verificación de certificados
- Certificado emitido por la CA → válido. ✔️
- Certificado expirado → inválido. ✔️
- Certificado alterado → inválido. ✔️
- Certificado revocado → inválido. ✔️

### 6.4 Validación del sistema (escenarios)
- Autenticación segura (JWT, contraseñas hasheadas). ✔️
- Cifrado/descifrado funcional; contraseña incorrecta → falla. ✔️
- Endpoints protegidos rechazan peticiones sin token (401). ✔️
- Pruebas desde Kali (Nmap): superficie de ataque mínima. [COMPLETAR con evidencia del lab]

---

## 7. Resultados

### 7.1 Tiempos promedio por operación (ms)

| Operación | 10 KB | 100 KB | 1 MB |
|-----------|-------|--------|------|
| Hash SHA-256 | 0.007 | 0.068 | 1.44 |
| Cifrado AES-256-GCM | 81.9 | 168.3 | 226.7 |
| Descifrado AES-256-GCM | 83.1 | 184.5 | 216.6 |
| Firma RSA-PSS | 40.1 | 130.7 | 224.0 |
| Verificación de firma | 0.12 | 0.36 | 1.56 |

Operaciones de costo fijo (media, ms): generación de claves RSA-2048 ≈ **401.5**;
emisión de certificado ≈ **544.6**; validación de certificado ≈ **191.4**; hash de
contraseña bcrypt ≈ **562.5**; verificación de contraseña ≈ **554.3**.

*(Ver figuras `analysis/results/fig_operaciones.png` y `fig_por_tamano.png`.)*

### 7.2 Tasas de detección y autenticación

| Métrica | Éxitos/Total | Tasa |
|---------|--------------|------|
| Detección por hash SHA-256 | 50/50 | **100 %** |
| Detección por firma digital | 50/50 | **100 %** |
| Detección por AES-GCM (tag) | 50/50 | **100 %** |
| Autenticación exitosa (clave correcta) | 15/15 | **100 %** |
| Rechazo correcto (clave incorrecta) | 15/15 | **100 %** |

*(Ver figura `analysis/results/fig_tasas.png`.)*

### 7.3 Análisis
- El **hash SHA-256** es la operación más rápida y escala linealmente con el tamaño,
  confirmándolo como mecanismo eficiente de integridad.
- Las operaciones deliberadamente lentas (**bcrypt ≈ 560 ms**, PBKDF2, generación RSA)
  tienen ese costo **por diseño**, para encarecer ataques de fuerza bruta.
- **Verificar** una firma es ~150 veces más rápido que **crearla** (1.56 ms vs 224 ms en
  1 MB), coherente con RSA (exponente público pequeño).
- Los tres mecanismos de detección de manipulación alcanzaron el **100 %** de efectividad.

---

## 8. Conclusiones

### 8.1 Aprendizajes
Se logró integrar en una sola plataforma los pilares de la criptografía aplicada —hash,
cifrado simétrico y asimétrico, firma digital y certificados con CA— dentro de un flujo
de desarrollo seguro (DevSecOps). El desarrollo incremental con verificación continua
(pruebas + análisis estático en cada commit) permitió mantener la calidad y detectar
errores de forma temprana.

### 8.2 Limitaciones
- La CA es **simulada** y de un solo nivel; no implementa listas de revocación (CRL/OCSP)
  ni cadenas intermedias.
- La gestión de claves privadas de usuario se delega al usuario (no hay custodia segura
  server-side con HSM).
- La autorización es por autenticación; no se implementó control de acceso por roles
  granular (RBAC) sobre todos los recursos.

### 8.3 Mejoras futuras
- Añadir **RBAC** y protección por roles a la gestión de usuarios.
- Incorporar revocación estándar (CRL/OCSP) y jerarquía de CA.
- Almacenamiento seguro de claves (cifrado en reposo / HSM).
- Ampliar el pipeline con pruebas dinámicas (DAST) y firma de imágenes.

---

## Referencias

[COMPLETAR — sugerencias]
- NIST FIPS 197 (AES), FIPS 186 (firma digital), FIPS 180-4 (SHA).
- RFC 5280 (X.509), RFC 8017 (RSA PKCS#1 / PSS).
- Documentación de FastAPI, de la librería `cryptography` y OWASP.
