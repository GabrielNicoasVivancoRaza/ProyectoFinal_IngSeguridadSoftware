# Entorno Virtualizado — Guía de Montaje

Red controlada para desplegar y probar la plataforma, según lo exige la rúbrica.

## Máquinas virtuales

| VM | Rol | RAM sugerida | Notas |
|----|-----|--------------|-------|
| **Ubuntu Server** | Backend + PostgreSQL + APIs criptográficas | 2 GB | Sin entorno gráfico |
| **Ubuntu Desktop** | Cliente legítimo (navegador con el frontend) | 2–4 GB | Con GUI |
| **Kali Linux** | Pentesting (Nmap, escaneos, validación de vulnerabilidades) | 2–4 GB | |
| **Metasploitable 2** | Objetivo vulnerable para análisis de riesgos | 512 MB–1 GB | **Nunca exponer a Internet** |

> Hypervisor recomendado: **VirtualBox** (o VMware). Las 4 VMs en la misma red interna.

## Configuración de red (host-only / red interna)

Usar una red **host-only** o **interna** para aislar el laboratorio. IPs fijas sugeridas:

| VM | IP | Puertos relevantes |
|----|----|--------------------|
| Ubuntu Server | `192.168.56.10` | 8000 (API), 5432 (PostgreSQL, solo interno) |
| Ubuntu Desktop | `192.168.56.11` | — (cliente) |
| Kali Linux | `192.168.56.20` | — (atacante) |
| Metasploitable 2 | `192.168.56.30` | múltiples (objetivo) |

### VirtualBox: crear la red host-only
1. `Archivo → Herramientas → Administrador de red host` → **Crear** (ej. `vboxnet0`, `192.168.56.1/24`).
2. En cada VM: `Configuración → Red → Adaptador 1 → Red solo-anfitrión (host-only)` → `vboxnet0`.
3. (Opcional) Adaptador 2 en NAT **solo** para Ubuntu Server/Desktop/Kali si necesitan instalar paquetes. **Metasploitable2 nunca con NAT.**

### Fijar IP en Ubuntu Server (netplan)
```yaml
# /etc/netplan/01-lab.yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: no
      addresses: [192.168.56.10/24]
```
```bash
sudo netplan apply
ip a          # verificar la IP
```

## Despliegue del backend en Ubuntu Server

Opción recomendada (Docker):
```bash
git clone <repo> && cd "Proyecto Final/infra"
cp .env.example .env       # ajustar POSTGRES_PASSWORD y SECRET_KEY
docker compose up -d --build
```

Verificar desde Ubuntu Desktop:
```bash
curl http://192.168.56.10:8000/health
# {"status":"ok",...}
```
Abrir el frontend (servido en Ubuntu Desktop o Server) apuntando `API_BASE` a `http://192.168.56.10:8000`.

## Verificación de conectividad

Desde Kali:
```bash
ping -c2 192.168.56.10      # Ubuntu Server
ping -c2 192.168.56.30      # Metasploitable2
```

## Checklist de montaje

- [ ] 4 VMs creadas e iniciadas.
- [ ] Red host-only con IPs fijas asignadas.
- [ ] Metasploitable2 **aislado** (sin NAT).
- [ ] Backend desplegado y respondiendo en `192.168.56.10:8000`.
- [ ] Frontend accesible desde Ubuntu Desktop.
- [ ] Kali con conectividad a Server y Metasploitable2.
