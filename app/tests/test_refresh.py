def get_tokens(client):
    client.post("/api/register", json={
        "username": "juan_dev",
        "email": "juan@test.com",
        "password": "MiP@ssw0rd!"
    })

    response = client.post("/api/login", json={
        "username": "juan_dev",
        "password": "MiP@ssw0rd!"
    })

    return response.json()


def test_refresh_success(client):
    tokens = get_tokens(client)

    response = client.post("/api/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_refresh_token_reuse(client):
    tokens = get_tokens(client)

    client.post("/api/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })

    response = client.post("/api/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Token de actualización ya utilizado"


def test_refresh_invalid_token(client):
    response = client.post("/api/refresh", json={
        "refresh_token": "invalid.token.value"
    })

    assert response.status_code == 401
