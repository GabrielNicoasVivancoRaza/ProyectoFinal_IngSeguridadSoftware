"""Pruebas del cifrado simetrico AES-256-GCM (servicio + endpoints)."""
import pytest
from cryptography.exceptions import InvalidTag

from app.crypto.symmetric import decrypt_bytes, encrypt_bytes

# --- Pruebas unitarias del servicio ---


def test_cifrado_descifrado_round_trip():
    original = b"documento confidencial 123"
    blob = encrypt_bytes(original, "claveSegura1")
    assert blob != original
    assert decrypt_bytes(blob, "claveSegura1") == original


def test_contrasena_incorrecta_falla():
    blob = encrypt_bytes(b"secreto", "claveSegura1")
    with pytest.raises(InvalidTag):
        decrypt_bytes(blob, "claveEquivocada9")


def test_dato_alterado_falla():
    blob = bytearray(encrypt_bytes(b"secreto", "claveSegura1"))
    blob[-1] ^= 0x01  # altera un byte del ciphertext/tag
    with pytest.raises(InvalidTag):
        decrypt_bytes(bytes(blob), "claveSegura1")


def test_blob_invalido_da_valueerror():
    with pytest.raises(ValueError):
        decrypt_bytes(b"corto", "claveSegura1")


# --- Pruebas de los endpoints ---


def test_encrypt_decrypt_endpoints(client, auth_headers):
    contenido = b"contenido a proteger"
    enc = client.post(
        "/crypto/encrypt",
        headers=auth_headers,
        data={"password": "claveSegura1"},
        files={"file": ("nota.txt", contenido, "text/plain")},
    )
    assert enc.status_code == 200
    assert enc.content != contenido

    dec = client.post(
        "/crypto/decrypt",
        headers=auth_headers,
        data={"password": "claveSegura1"},
        files={"file": ("nota.txt.enc", enc.content, "application/octet-stream")},
    )
    assert dec.status_code == 200
    assert dec.content == contenido


def test_decrypt_con_password_incorrecta_da_400(client, auth_headers):
    enc = client.post(
        "/crypto/encrypt",
        headers=auth_headers,
        data={"password": "claveSegura1"},
        files={"file": ("nota.txt", b"hola", "text/plain")},
    )
    dec = client.post(
        "/crypto/decrypt",
        headers=auth_headers,
        data={"password": "otraClave9999"},
        files={"file": ("nota.txt.enc", enc.content, "application/octet-stream")},
    )
    assert dec.status_code == 400


def test_encrypt_requiere_autenticacion(client):
    resp = client.post(
        "/crypto/encrypt",
        data={"password": "claveSegura1"},
        files={"file": ("nota.txt", b"hola", "text/plain")},
    )
    assert resp.status_code == 401
