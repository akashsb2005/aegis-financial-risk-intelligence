def _register(client, account_data):
    return client.post(
        "/api/v1/auth/register",
        json={
            "full_name": account_data.full_name,
            "email": account_data.email,
            "password": account_data.password,
        },
    )


def _login(client, account_data, password=None):
    return client.post(
        "/api/v1/auth/login",
        json={
            "email": account_data.email,
            "password": password or account_data.password,
        },
    )


def test_registration_returns_safe_analyst_user(client, account_data):
    response = _register(client, account_data)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"user"}
    assert body["user"]["full_name"] == account_data.full_name
    assert body["user"]["email"] == account_data.email
    assert body["user"]["role"] == "ANALYST"
    assert isinstance(body["user"]["user_id"], int)
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_duplicate_registration_is_rejected(client, account_data):
    assert _register(client, account_data).status_code == 201

    response = _register(client, account_data)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


def test_login_returns_bearer_session(client, registered_account):
    response = _login(client, registered_account)

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert isinstance(body["expires_at"], str)
    assert body["user"]["email"] == registered_account.email
    assert body["user"]["role"] == "ANALYST"


def test_invalid_login_is_rejected(client, account_data):
    response = _login(client, account_data)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_company_list_requires_authentication(client):
    response = client.get("/api/v1/companies")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


def test_logout_revokes_previously_valid_session(authenticated_client):
    session = authenticated_client
    before_logout = session.client.get(
        "/api/v1/companies",
        headers=session.headers,
    )
    assert before_logout.status_code == 200

    logout_response = session.client.post(
        "/api/v1/auth/logout",
        headers=session.headers,
    )
    assert logout_response.status_code == 200
    assert logout_response.json() == {"message": "Logged out successfully."}

    after_logout = session.client.get(
        "/api/v1/companies",
        headers=session.headers,
    )
    assert after_logout.status_code == 401
    assert after_logout.json()["error"]["code"] == "UNAUTHENTICATED"
