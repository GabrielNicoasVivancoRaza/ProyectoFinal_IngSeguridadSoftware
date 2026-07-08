"""Pruebas del CRUD de documentos y de la verificacion de integridad por hash."""
import hashlib


def _subir_documento(client, headers, contenido=b"contenido de prueba", nombre="doc.txt"):
    return client.post(
        "/documents",
        headers=headers,
        files={"file": (nombre, contenido, "text/plain")},
    )


def test_subir_requiere_autenticacion(client):
    resp = _subir_documento(client, headers={})
    assert resp.status_code == 401


def test_subir_documento_calcula_sha256(client, auth_headers):
    contenido = b"hola mundo"
    resp = _subir_documento(client, auth_headers, contenido=contenido)
    assert resp.status_code == 201
    body = resp.json()
    assert body["filename"] == "doc.txt"
    assert body["sha256"] == hashlib.sha256(contenido).hexdigest()


def test_verificar_integridad_ok(client, auth_headers):
    doc = _subir_documento(client, auth_headers).json()
    resp = client.get(f"/documents/{doc['id']}/verify", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is True
    assert body["actual_sha256"] == body["stored_sha256"]


def test_verificar_detecta_alteracion(client, auth_headers, tmp_path):
    """Si el archivo en disco cambia, el hash ya no coincide -> integridad invalida."""
    doc = _subir_documento(client, auth_headers, contenido=b"original").json()

    # Localiza el archivo almacenado y lo altera.
    storage = tmp_path / "storage"
    archivo = next(storage.iterdir())
    archivo.write_bytes(b"contenido alterado")

    resp = client.get(f"/documents/{doc['id']}/verify", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


def test_eliminacion_logica_documento(client, auth_headers):
    doc = _subir_documento(client, auth_headers).json()
    assert client.delete(f"/documents/{doc['id']}", headers=auth_headers).status_code == 204

    assert client.get("/documents", headers=auth_headers).json() == []
    incluidos = client.get("/documents?include_deleted=true", headers=auth_headers).json()
    assert len(incluidos) == 1
    assert incluidos[0]["is_deleted"] is True
