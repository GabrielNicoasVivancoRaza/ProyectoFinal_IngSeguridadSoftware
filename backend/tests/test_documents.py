"""Pruebas del CRUD de documentos y de la verificacion de integridad por hash."""
import hashlib


def _crear_usuario(client):
    return client.post(
        "/users",
        json={"username": "bob", "email": "bob@example.com", "password": "supersegura1"},
    ).json()


def _subir_documento(client, user_id, contenido=b"contenido de prueba", nombre="doc.txt"):
    return client.post(
        "/documents",
        data={"user_id": user_id},
        files={"file": (nombre, contenido, "text/plain")},
    )


def test_subir_documento_calcula_sha256(client):
    user = _crear_usuario(client)
    contenido = b"hola mundo"
    resp = _subir_documento(client, user["id"], contenido=contenido)
    assert resp.status_code == 201
    body = resp.json()
    assert body["filename"] == "doc.txt"
    assert body["sha256"] == hashlib.sha256(contenido).hexdigest()


def test_subir_para_usuario_inexistente_da_404(client):
    resp = _subir_documento(client, 999)
    assert resp.status_code == 404


def test_verificar_integridad_ok(client):
    user = _crear_usuario(client)
    doc = _subir_documento(client, user["id"]).json()
    resp = client.get(f"/documents/{doc['id']}/verify")
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is True
    assert body["actual_sha256"] == body["stored_sha256"]


def test_verificar_detecta_alteracion(client, tmp_path):
    """Si el archivo en disco cambia, el hash ya no coincide -> integridad invalida."""
    user = _crear_usuario(client)
    doc = _subir_documento(client, user["id"], contenido=b"original").json()

    # Localiza el archivo almacenado y lo altera.
    storage = tmp_path / "storage"
    archivo = next(storage.iterdir())
    archivo.write_bytes(b"contenido alterado")

    resp = client.get(f"/documents/{doc['id']}/verify")
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


def test_eliminacion_logica_documento(client):
    user = _crear_usuario(client)
    doc = _subir_documento(client, user["id"]).json()
    assert client.delete(f"/documents/{doc['id']}").status_code == 204

    assert client.get("/documents").json() == []
    incluidos = client.get("/documents?include_deleted=true").json()
    assert len(incluidos) == 1
    assert incluidos[0]["is_deleted"] is True
