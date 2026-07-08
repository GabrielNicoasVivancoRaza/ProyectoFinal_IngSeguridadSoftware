"""Pruebas del flujo de autenticacion (registro, login con JWT y perfil)."""


def _registrar(client):
    return client.post(
        "/auth/register",
        json={"username": "carol", "email": "carol@example.com", "password": "supersegura1"},
    )


def test_registro_y_login(client):
    assert _registrar(client).status_code == 201

    resp = client.post(
        "/auth/login", data={"username": "carol", "password": "supersegura1"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_credenciales_incorrectas(client):
    _registrar(client)
    resp = client.post(
        "/auth/login", data={"username": "carol", "password": "claveerronea"}
    )
    assert resp.status_code == 401


def test_me_requiere_token(client):
    assert client.get("/auth/me").status_code == 401


def test_me_devuelve_usuario_autenticado(client):
    _registrar(client)
    token = client.post(
        "/auth/login", data={"username": "carol", "password": "supersegura1"}
    ).json()["access_token"]

    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "carol"


def test_token_invalido_es_rechazado(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer token.falso.aqui"})
    assert resp.status_code == 401
