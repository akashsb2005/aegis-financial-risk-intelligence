from uuid import uuid4

import pytest
from sqlalchemy import text

from app.core.database import engine


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


def test_authenticated_company_audit_history_returns_trigger_record(
    authenticated_client,
    company,
):
    session = authenticated_client
    create_response = session.client.post(
        f"/api/v1/companies/{company.company_id}/risk-assessments",
        headers=session.headers,
        json=_assessment_payload(),
    )
    assert create_response.status_code == 201, create_response.text
    assessment_id = create_response.json()["risk_assessment_id"]

    with engine.connect() as connection:
        audit_row = connection.execute(
            text(
                """
                SELECT audit_id, risk_assessment_id, company_id, risk_score,
                       logged_at, action_type, risk_level, model_version,
                       explanation, assessed_by
                FROM public.risk_assessment_audit
                WHERE risk_assessment_id = :assessment_id
                """
            ),
            {"assessment_id": assessment_id},
        ).mappings().one()

    response = session.client.get(
        f"/api/v1/companies/{company.company_id}/audit-history",
        headers=session.headers,
    )

    assert response.status_code == 200
    history = response.json()
    assert len(history) == 1
    record = history[0]
    assert set(record) == {
        "audit_id",
        "risk_assessment_id",
        "company_id",
        "risk_score",
        "logged_at",
        "action_type",
        "risk_level",
        "model_version",
        "explanation",
        "assessed_by",
    }
    assert record["audit_id"] == audit_row["audit_id"]
    assert record["risk_assessment_id"] == audit_row["risk_assessment_id"]
    assert record["company_id"] == audit_row["company_id"] == company.company_id
    assert record["risk_score"] == str(audit_row["risk_score"])
    assert record["logged_at"] == audit_row["logged_at"].isoformat()
    assert record["action_type"] == audit_row["action_type"] == "INSERT"
    assert record["risk_level"] == audit_row["risk_level"] == "HIGH"
    assert record["model_version"] == audit_row["model_version"] == "api-test-1"
    assert record["explanation"] == audit_row["explanation"]
    assert record["assessed_by"] == audit_row["assessed_by"] == session.user_id


def test_company_audit_history_is_scoped_to_requested_company(
    authenticated_client,
    company,
):
    session = authenticated_client
    registration_number = f"AEGIS-API-TEST-{uuid4().hex}"
    with engine.begin() as connection:
        company_b_id = connection.execute(
            text(
                """
                INSERT INTO public.companies
                    (company_name, registration_number, industry, country,
                     annual_revenue, employee_count)
                VALUES
                    ('AEGIS Audit Scope Test B', :registration_number,
                     'Testing', 'IN', 12345.67, 10)
                RETURNING company_id
                """
            ),
            {"registration_number": registration_number},
        ).scalar_one()

    assessment_a_response = session.client.post(
        f"/api/v1/companies/{company.company_id}/risk-assessments",
        headers=session.headers,
        json=_assessment_payload(model_version="audit-scope-company-a"),
    )
    assert assessment_a_response.status_code == 201, assessment_a_response.text
    assessment_a_id = assessment_a_response.json()["risk_assessment_id"]

    assessment_b_response = session.client.post(
        f"/api/v1/companies/{company_b_id}/risk-assessments",
        headers=session.headers,
        json=_assessment_payload(model_version="audit-scope-company-b"),
    )
    assert assessment_b_response.status_code == 201, assessment_b_response.text
    assessment_b_id = assessment_b_response.json()["risk_assessment_id"]

    history_a_response = session.client.get(
        f"/api/v1/companies/{company.company_id}/audit-history",
        headers=session.headers,
    )
    history_b_response = session.client.get(
        f"/api/v1/companies/{company_b_id}/audit-history",
        headers=session.headers,
    )

    assert history_a_response.status_code == 200
    history_a = history_a_response.json()
    assert any(record["risk_assessment_id"] == assessment_a_id for record in history_a)
    assert all(record["company_id"] == company.company_id for record in history_a)
    assert all(record["risk_assessment_id"] != assessment_b_id for record in history_a)

    assert history_b_response.status_code == 200
    history_b = history_b_response.json()
    assert any(record["risk_assessment_id"] == assessment_b_id for record in history_b)
    assert all(record["company_id"] == company_b_id for record in history_b)
    assert all(record["risk_assessment_id"] != assessment_a_id for record in history_b)


def test_company_audit_history_is_empty_without_assessments(
    authenticated_client,
    company,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{company.company_id}/audit-history",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_company_audit_history_returns_not_found_for_missing_company(
    authenticated_client,
):
    response = authenticated_client.client.get(
        "/api/v1/companies/2147483647/audit-history",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "COMPANY_NOT_FOUND"


def test_company_audit_history_requires_authentication(client, company):
    response = client.get(f"/api/v1/companies/{company.company_id}/audit-history")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


def test_admin_can_read_company_audit_history(admin_authenticated_client, company):
    response = admin_authenticated_client.client.get(
        f"/api/v1/companies/{company.company_id}/audit-history",
        headers=admin_authenticated_client.headers,
    )

    assert response.status_code == 200
    assert response.json() == []


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


def test_authenticated_audit_history_returns_database_trigger_snapshot(
    authenticated_client,
    company,
):
    session = authenticated_client
    create_response = session.client.post(
        f"/api/v1/companies/{company.company_id}/risk-assessments",
        headers=session.headers,
        json=_assessment_payload(),
    )
    assert create_response.status_code == 201, create_response.text
    assessment = create_response.json()

    response = session.client.get(
        f"/api/v1/companies/{company.company_id}/risk-audit-history",
        headers=session.headers,
    )

    assert response.status_code == 200, response.text
    entries = response.json()
    assert len(entries) == 1
    audit = entries[0]
    assert audit["risk_assessment_id"] == assessment["risk_assessment_id"]
    assert audit["company_id"] == company.company_id
    assert audit["risk_score"] == "72.50"
    assert audit["risk_level"] == "HIGH"
    assert audit["action_type"] == "INSERT"
    assert audit["model_version"] == "api-test-1"
    assert audit["explanation"] == "Synthetic integration-test assessment."
    assert audit["assessed_by"] == session.user_id
    assert isinstance(audit["logged_at"], str)


def test_audit_history_requires_authentication(client, company):
    response = client.get(
        f"/api/v1/companies/{company.company_id}/risk-audit-history"
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


def test_audit_history_returns_not_found_for_missing_company(
    authenticated_client,
):
    response = authenticated_client.client.get(
        "/api/v1/companies/2147483647/risk-audit-history",
        headers=authenticated_client.headers,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "COMPANY_NOT_FOUND"


def test_audit_history_supports_pagination(authenticated_client, company):
    session = authenticated_client
    for score in ("21.00", "42.00", "63.00"):
        response = session.client.post(
            f"/api/v1/companies/{company.company_id}/risk-assessments",
            headers=session.headers,
            json=_assessment_payload(risk_score=score),
        )
        assert response.status_code == 201, response.text

    response = session.client.get(
        f"/api/v1/companies/{company.company_id}/risk-audit-history?limit=2&offset=1",
        headers=session.headers,
    )
    assert response.status_code == 200, response.text
    assert len(response.json()) == 2
