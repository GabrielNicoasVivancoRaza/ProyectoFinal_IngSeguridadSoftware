"""Pruebas de RSA: generacion de claves y firma digital (servicio + endpoints)."""
from app.crypto.asymmetric import generate_keypair, sign, verify

# --- Pruebas unitarias del servicio ---


def test_generar_par_de_claves():
    priv, pub = generate_keypair()
    assert "BEGIN PRIVATE KEY" in priv
    assert "BEGIN PUBLIC KEY" in pub


def test_firma_valida():
    priv, pub = generate_keypair()
    data = b"documento importante"
    firma = sign(data, priv)
    assert verify(data, firma, pub) is True


def test_documento_alterado_invalida_la_firma():
    priv, pub = generate_keypair()
    firma = sign(b"documento original", priv)
    assert verify(b"documento MODIFICADO", firma, pub) is False


def test_firma_de_otra_clave_es_invalida():
    priv1, _ = generate_keypair()
    _, pub2 = generate_keypair()
    firma = sign(b"data", priv1)
    assert verify(b"data", firma, pub2) is False


# --- Pruebas de los endpoints ---


def test_flujo_completo_firma(client, auth_headers):
    # 1. Generar claves
    claves = client.post("/crypto/keys/generate", headers=auth_headers).json()

    # 2. Firmar un documento
    contenido = b"contrato digital"
    firma = client.post(
        "/crypto/sign",
        headers=auth_headers,
        data={"private_key_pem": claves["private_key_pem"]},
        files={"file": ("contrato.txt", contenido, "text/plain")},
    ).json()
    assert firma["algorithm"] == "RSA-PSS-SHA256"

    # 3. Verificar la firma sobre el documento intacto -> valida
    ok = client.post(
        "/crypto/verify",
        headers=auth_headers,
        data={
            "public_key_pem": claves["public_key_pem"],
            "signature_b64": firma["signature_b64"],
        },
        files={"file": ("contrato.txt", contenido, "text/plain")},
    ).json()
    assert ok["valid"] is True

    # 4. Verificar sobre un documento alterado -> invalida
    alterado = client.post(
        "/crypto/verify",
        headers=auth_headers,
        data={
            "public_key_pem": claves["public_key_pem"],
            "signature_b64": firma["signature_b64"],
        },
        files={"file": ("contrato.txt", b"contrato ALTERADO", "text/plain")},
    ).json()
    assert alterado["valid"] is False


def test_generar_claves_requiere_autenticacion(client):
    assert client.post("/crypto/keys/generate").status_code == 401
