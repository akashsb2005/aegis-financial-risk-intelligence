def test_authenticated_financial_records_are_ordered_and_preserve_decimals(
    authenticated_client,
    company,
    insert_financial_record,
):
    insert_financial_record(company.company_id, 2024, "2400.00")
    insert_financial_record(company.company_id, 2025, "2500.00")

    response = authenticated_client.client.get(
        f"/api/v1/companies/{company.company_id}/financial-records",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    records = response.json()
    assert [record["fiscal_year"] for record in records] == [2025, 2024]
    assert records[0]["revenue"] == "2500.00"
    assert records[1]["revenue"] == "2400.00"
    assert set(records[0]) == {
        "financial_record_id",
        "company_id",
        "fiscal_year",
        "revenue",
        "net_profit",
        "total_assets",
        "total_liabilities",
        "total_debt",
        "shareholders_equity",
        "operating_cash_flow",
        "created_at",
    }
    assert records[0]["company_id"] == company.company_id
    assert isinstance(records[0]["financial_record_id"], int)
    assert isinstance(records[0]["created_at"], str)
    for field in (
        "revenue",
        "net_profit",
        "total_assets",
        "total_liabilities",
        "total_debt",
        "shareholders_equity",
        "operating_cash_flow",
    ):
        assert isinstance(records[0][field], str)


def test_financial_records_require_authentication(client, company):
    response = client.get(
        f"/api/v1/companies/{company.company_id}/financial-records",
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


def test_financial_records_return_not_found_for_missing_company(authenticated_client):
    response = authenticated_client.client.get(
        "/api/v1/companies/2147483647/financial-records",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "COMPANY_NOT_FOUND"


def test_company_without_financial_records_returns_empty_list(
    authenticated_client,
    company,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{company.company_id}/financial-records",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    assert response.json() == []
