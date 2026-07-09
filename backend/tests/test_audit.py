"""Pruebas del registro de auditoria."""


def test_login_genera_evento_de_auditoria(client, auth_headers):
    # auth_headers ya realizo un registro + login exitoso.
    logs = client.get("/audit/logs", headers=auth_headers).json()
    eventos = {log["event_type"] for log in logs}
    assert "register" in eventos
    assert "login" in eventos


def test_login_fallido_se_registra(client):
    client.post(
        "/auth/register",
        json={"username": "dora", "email": "dora@example.com", "password": "supersegura1"},
    )
    client.post("/auth/login", data={"username": "dora", "password": "claveMala123"})
    token = client.post(
        "/auth/login", data={"username": "dora", "password": "supersegura1"}
    ).json()["access_token"]

    logs = client.get(
        "/audit/logs", headers={"Authorization": f"Bearer {token}"}
    ).json()
    assert any(log["event_type"] == "login_failed" for log in logs)


def test_eventos_criptograficos_se_registran(client, auth_headers):
    # Subir documento y emitir certificado deben quedar auditados.
    client.post(
        "/documents",
        headers=auth_headers,
        files={"file": ("x.txt", b"hola", "text/plain")},
    )
    client.post("/certificates", headers=auth_headers)

    eventos = {
        log["event_type"] for log in client.get("/audit/logs", headers=auth_headers).json()
    }
    assert "document_upload" in eventos
    assert "cert_issue" in eventos


def test_logs_requieren_autenticacion(client):
    assert client.get("/audit/logs").status_code == 401
