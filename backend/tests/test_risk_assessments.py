import pytest


def _assessment_payload(**overrides):
    return {
        "risk_score": "72.50",
        "risk_level": "HIGH",
        "model_version": "api-test-1",
        "explanation": "Synthetic integration-test assessment.",
        **overrides,
    }


def test_authenticated_risk_summary_returns_empty_summary(
    authenticated_client,
    company,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{company.company_id}/risk-summary",
        headers=authenticated_client.headers,
    )
    assert response.status_code == 200
    assert response.status_code == 200
    summary = response.json()
    assert summary["company_id"] == company.company_id
    assert isinstance(summary["company_name"], str)
    assert summary["current_risk_level"] is None
    assert summary["current_risk_score"] is None
    assert summary["assessed_at"] is None
    assert summary["model_version"] is None


def test_authenticated_risk_history_returns_assessment_array(
    authenticated_client,
    company,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{company.company_id}/risk-assessments",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    "path_suffix",
    ["risk-summary", "risk-assessments"],
)
def test_risk_reads_return_not_found_for_missing_company(
    authenticated_client,
    path_suffix,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/2147483647/{path_suffix}",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "COMPANY_NOT_FOUND"


@pytest.mark.parametrize(
    "path_suffix",
    ["risk-summary", "risk-assessments"],
)
def test_risk_reads_require_authentication(client, company, path_suffix):
    response = client.get(
        f"/api/v1/companies/{company.company_id}/{path_suffix}",
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


def test_analyst_can_create_assessment_and_history_includes_it(
    authenticated_client,
    company,
):
    session = authenticated_client
    create_response = session.client.post(
        f"/api/v1/companies/{company.company_id}/risk-assessments",
        headers=session.headers,
        json=_assessment_payload(assessed_by=2147483647),
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert set(created) == {
        "risk_assessment_id",
        "company_id",
        "risk_score",
        "risk_level",
        "assessed_at",
        "model_version",
        "explanation",
        "assessed_by",
    }
    assert isinstance(created["risk_assessment_id"], int)
    assert created["company_id"] == company.company_id
    assert created["risk_score"] == "72.50"
    assert created["risk_level"] == "HIGH"
    assert isinstance(created["assessed_at"], str)
    assert created["model_version"] == "api-test-1"
    assert created["explanation"] == "Synthetic integration-test assessment."
    assert created["assessed_by"] == session.user_id

    history_response = session.client.get(
        f"/api/v1/companies/{company.company_id}/risk-assessments",
        headers=session.headers,
    )
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["risk_assessment_id"] == created["risk_assessment_id"]

    summary_response = session.client.get(
        f"/api/v1/companies/{company.company_id}/risk-summary",
        headers=session.headers,
    )
    assert summary_response.status_code == 200
    assert summary_response.json()["current_risk_level"] == "HIGH"
    assert summary_response.json()["current_risk_score"] == "72.50"


@pytest.mark.parametrize(
    "overrides",
    [
        {"risk_score": "100.01"},
        {"risk_score": "-0.01"},
    ],
)
def test_invalid_risk_score_is_rejected(
    authenticated_client,
    company,
    overrides,
):
    response = authenticated_client.client.post(
        f"/api/v1/companies/{company.company_id}/risk-assessments",
        headers=authenticated_client.headers,
        json=_assessment_payload(**overrides),
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_invalid_risk_level_is_rejected(authenticated_client, company):
    response = authenticated_client.client.post(
        f"/api/v1/companies/{company.company_id}/risk-assessments",
        headers=authenticated_client.headers,
        json=_assessment_payload(risk_level="EXTREME"),
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_only_analyst_can_create_assessments(
    admin_authenticated_client,
    company,
):
    response = admin_authenticated_client.client.post(
        f"/api/v1/companies/{company.company_id}/risk-assessments",
        headers=admin_authenticated_client.headers,
        json=_assessment_payload(),
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
