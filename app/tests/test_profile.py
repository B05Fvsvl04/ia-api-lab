def authenticate(client):
    client.post("/api/register", json={
        "username": "juan_dev",
        "email": "juan@test.com",
        "password": "MiP@ssw0rd!"
    })

    login = client.post("/api/login", json={
        "username": "juan_dev",
        "password": "MiP@ssw0rd!"
    })

    return login.json()["access_token"]


def test_get_profile_success(client):
    token = authenticate(client)

    response = client.get(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["username"] == "juan_dev"


def test_get_profile_unauthenticated(client):
    response = client.get("/api/profile")

    assert response.status_code == 403 or response.status_code == 401


def test_update_profile_email(client):
    token = authenticate(client)

    response = client.put(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "nuevo@test.com"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "nuevo@test.com"


def test_update_profile_duplicate_email(client):
    client.post("/api/register", json={
        "username": "user1",
        "email": "a@test.com",
        "password": "MiP@ssw0rd!"
    })

    token = authenticate(client)

    response = client.put(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "a@test.com"}
    )

    assert response.status_code == 409
