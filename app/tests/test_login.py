def create_user(client):
    client.post("/api/register", json={
        "username": "juan_dev",
        "email": "juan@test.com",
        "password": "MiP@ssw0rd!"
    })


def test_login_success(client):
    create_user(client)

    response = client.post("/api/login", json={
        "username": "juan_dev",
        "password": "MiP@ssw0rd!"
    })

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password(client):
    create_user(client)

    response = client.post("/api/login", json={
        "username": "juan_dev",
        "password": "WrongPass123!"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales incorrectas"


def test_login_nonexistent_user(client):
    response = client.post("/api/login", json={
        "username": "no_user",
        "password": "Whatever123!"
    })

    assert response.status_code == 401
