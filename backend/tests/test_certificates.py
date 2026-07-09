"""Pruebas de la CA simulada y los certificados digitales (servicio + endpoints)."""
from app.crypto.ca import issue_certificate, validate_certificate

# --- Pruebas unitarias de la CA ---


def test_certificado_emitido_es_valido():
    _, _, cert_pem, _, _ = issue_certificate("usuario_prueba")
    valido, _ = validate_certificate(cert_pem)
    assert valido is True


def test_certificado_expirado_es_invalido():
    _, _, cert_pem, _, _ = issue_certificate("usuario_prueba", validity_days=-1)
    valido, detalle = validate_certificate(cert_pem)
    assert valido is False
    assert "expirado" in detalle


def test_certificado_alterado_es_invalido():
    _, _, cert_pem, _, _ = issue_certificate("usuario_prueba")
    # Altera el contenido del certificado (una linea del cuerpo base64).
    lineas = cert_pem.splitlines()
    lineas[2] = lineas[2][:-4] + "AAAA"
    alterado = "\n".join(lineas)
    valido, _ = validate_certificate(alterado)
    assert valido is False


# --- Pruebas de los endpoints ---


def test_emitir_y_validar_certificado(client, auth_headers):
    emitido = client.post("/certificates", headers=auth_headers).json()
    assert emitido["status"] == "valid"
    assert "BEGIN CERTIFICATE" in emitido["cert_pem"]
    assert "BEGIN PRIVATE KEY" in emitido["private_key_pem"]

    val = client.get(f"/certificates/{emitido['id']}/validate", headers=auth_headers).json()
    assert val["valid"] is True


def test_revocar_certificado(client, auth_headers):
    emitido = client.post("/certificates", headers=auth_headers).json()
    rev = client.post(f"/certificates/{emitido['id']}/revoke", headers=auth_headers).json()
    assert rev["status"] == "revoked"

    val = client.get(f"/certificates/{emitido['id']}/validate", headers=auth_headers).json()
    assert val["valid"] is False
    assert "revocado" in val["detail"]


def test_emitir_requiere_autenticacion(client):
    assert client.post("/certificates").status_code == 401
