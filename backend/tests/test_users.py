"""Pruebas del CRUD de usuarios."""


def _nuevo_usuario(client, username="alice", email="alice@example.com"):
    return client.post(
        "/users",
        json={"username": username, "email": email, "password": "supersegura1"},
    )


def test_crear_usuario(client):
    resp = _nuevo_usuario(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "alice"
    assert body["is_active"] is True
    # La contrasena o su hash nunca deben exponerse en la respuesta.
    assert "password" not in body
    assert "password_hash" not in body


def test_no_permite_username_duplicado(client):
    _nuevo_usuario(client)
    resp = _nuevo_usuario(client, email="otro@example.com")
    assert resp.status_code == 409


def test_listar_y_obtener_usuario(client):
    creado = _nuevo_usuario(client).json()
    assert client.get("/users").json()[0]["id"] == creado["id"]

    resp = client.get(f"/users/{creado['id']}")
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"


def test_obtener_inexistente_da_404(client):
    assert client.get("/users/999").status_code == 404


def test_actualizar_usuario(client):
    creado = _nuevo_usuario(client).json()
    resp = client.put(f"/users/{creado['id']}", json={"role": "admin"})
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


def test_eliminacion_logica(client):
    creado = _nuevo_usuario(client).json()
    assert client.delete(f"/users/{creado['id']}").status_code == 204

    # Ya no aparece en el listado normal...
    assert client.get("/users").json() == []
    # ...pero sigue existiendo (borrado logico) y aparece con include_inactive.
    inactivos = client.get("/users?include_inactive=true").json()
    assert len(inactivos) == 1
    assert inactivos[0]["is_active"] is False
