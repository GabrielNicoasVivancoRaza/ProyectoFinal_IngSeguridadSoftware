# Pruebas de Seguridad desde Kali Linux

Procedimiento de escaneo y análisis controlado. Ejecuta los comandos desde **Kali**
(`192.168.56.20`) y **pega la salida real** en las secciones "Resultado".

> ⚠️ Solo sobre las VMs del laboratorio. Escanear equipos ajenos es ilegal.

---

## 1. Escaneo Nmap del Backend (Ubuntu Server)

### 1.1 Descubrimiento de puertos y servicios
```bash
nmap -sV -sC -p- 192.168.56.10 -oN nmap_server.txt
```
- `-sV` detecta versiones, `-sC` corre scripts por defecto, `-p-` todos los puertos.

**Resultado esperado:** solo debería verse el puerto **8000/tcp** (API). Postgres (5432)
**no** debe estar accesible desde la red si se configuró bien (solo interno al contenedor).

**Resultado (pegar salida real):**
```
<pegar aquí la salida de nmap_server.txt>
```

### 1.2 Detección de sistema operativo
```bash
sudo nmap -O 192.168.56.10 -oN nmap_os.txt
```
**Resultado (pegar salida real):**
```
<pegar aquí>
```

### 1.3 Verificación de cabeceras HTTP de la API
```bash
nmap --script http-headers -p 8000 192.168.56.10
curl -I http://192.168.56.10:8000/health
```
**Análisis:** anotar si aparecen cabeceras que revelen tecnología/versión (superficie de ataque).

---

## 2. Análisis de Metasploitable 2 (objetivo vulnerable)

Metasploitable2 se usa para **demostrar el proceso de detección**, comparándolo con lo
"blindado" que está el backend propio.

```bash
nmap -sV -p- 192.168.56.30 -oN nmap_metasploitable.txt
```

**Resultado esperado:** decenas de puertos abiertos con servicios **obsoletos y vulnerables**
(vsftpd 2.3.4, Samba, distcc, etc.).

**Resultado (pegar salida real):**
```
<pegar aquí la salida — evidencia del contraste con el backend endurecido>
```

### 2.1 Escaneo de vulnerabilidades con scripts NSE
```bash
nmap --script vuln 192.168.56.30 -oN nmap_vuln.txt
```
**Resultado (pegar salida real):**
```
<pegar aquí — Nmap señalará CVEs conocidos>
```

---

## 3. Pruebas dirigidas a la plataforma

### 3.1 Endpoints protegidos requieren autenticación
```bash
# Sin token -> debe responder 401
curl -s -o /dev/null -w "%{http_code}\n" http://192.168.56.10:8000/documents
curl -s -o /dev/null -w "%{http_code}\n" http://192.168.56.10:8000/certificates
```
**Resultado esperado:** `401` en ambos. **Resultado real:** `___` / `___`

### 3.2 Contraseñas nunca viajan/almacenan en claro
- Registrar un usuario y confirmar en la BD (pgAdmin4) que `password_hash` es un hash bcrypt (`$2b$...`), no la contraseña.
- La respuesta de la API **no** incluye `password` ni `password_hash` (verificado por pruebas automáticas).

### 3.3 Detección de manipulación (demostración en vivo)
- Subir un documento → verificar → **válido**.
- Alterar el archivo en disco → verificar → **inválido** (hash distinto).
- Firmar un documento → modificarlo → verificar firma → **inválida**.

---

## 4. Resumen de la superficie de ataque

| Host | Puertos abiertos | Servicios | Observación |
|------|------------------|-----------|-------------|
| Ubuntu Server (backend) | 8000 | HTTP/API | Superficie mínima |
| Metasploitable2 | (llenar) | (llenar) | Múltiples servicios vulnerables |

**Conclusión:** el backend expone una superficie de ataque **mínima** (un solo puerto,
autenticación obligatoria, sin servicios heredados), en contraste con Metasploitable2.
