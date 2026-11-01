def test_authenticated_company_list_has_valid_response_schema(
    authenticated_client,
    company,
):
    response = authenticated_client.client.get(
        "/api/v1/companies",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    companies = response.json()
    assert isinstance(companies, list)
    result = next(
        item for item in companies if item["company_id"] == company.company_id
    )
    assert set(result) == {
        "company_id",
        "company_name",
        "registration_number",
        "industry",
        "country",
        "annual_revenue",
        "employee_count",
        "created_at",
        "updated_at",
    }
    assert isinstance(result["company_id"], int)
    assert isinstance(result["company_name"], str)
    assert isinstance(result["registration_number"], str)
    assert isinstance(result["annual_revenue"], str)
    assert isinstance(result["employee_count"], int)
    assert isinstance(result["created_at"], str)
    assert isinstance(result["updated_at"], str)


def test_company_list_supports_limit_and_offset(authenticated_client):
    response = authenticated_client.client.get(
        "/api/v1/companies?limit=1&offset=0",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_company_list_rejects_invalid_pagination(authenticated_client):
    response = authenticated_client.client.get(
        "/api/v1/companies?limit=0",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_company_detail_rejects_non_positive_id(authenticated_client):
    response = authenticated_client.client.get(
        "/api/v1/companies/0",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 422


def test_company_detail_returns_not_found_for_missing_id(authenticated_client):
    response = authenticated_client.client.get(
        "/api/v1/companies/2147483647",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "COMPANY_NOT_FOUND"
