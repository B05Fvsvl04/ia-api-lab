def test_register_success(client):
    response = client.post("/api/register", json={
        "username": "juan_dev",
        "email": "juan@test.com",
        "password": "MiP@ssw0rd!"
    })

    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["username"] == "juan_dev"
    assert body["email"] == "juan@test.com"


def test_register_duplicate_username(client):
    client.post("/api/register", json={
        "username": "juan_dev",
        "email": "juan@test.com",
        "password": "MiP@ssw0rd!"
    })

    response = client.post("/api/register", json={
        "username": "juan_dev",
        "email": "otro@test.com",
        "password": "MiP@ssw0rd!"
    })

    assert response.status_code == 409


def test_register_invalid_password(client):
    response = client.post("/api/register", json={
        "username": "bad_user",
        "email": "bad@test.com",
        "password": "123"
    })

    assert response.status_code == 422
