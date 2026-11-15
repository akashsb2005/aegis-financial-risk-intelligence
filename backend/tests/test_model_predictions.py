from sqlalchemy import text

from app.core.database import engine


def test_predictions_require_authentication(client, company):
    response = client.get(f"/api/v1/companies/{company.company_id}/predictions")
    assert response.status_code == 401


def test_predictions_are_company_scoped_and_filterable(
    authenticated_client, company
):
    with engine.begin() as connection:
        security_id = connection.execute(
            text(
                """INSERT INTO public.securities
                   (company_id, ticker, exchange, asset_type, currency)
                   VALUES (:company_id, :ticker, 'TEST', 'EQUITY', 'INR')
                   RETURNING security_id"""
            ),
            {"company_id": company.company_id, "ticker": f"TST{company.company_id}"},
        ).scalar_one()
        connection.execute(
            text(
                """INSERT INTO public.model_predictions
                   (security_id, prediction_type, prediction_date,
                    predicted_value, signal, model_name, model_version)
                   VALUES
                   (:security_id, 'ANOMALY', DATE '2026-01-02', -0.12,
                    'ANOMALY', 'test-isolation-forest', 'test-1'),
                   (:security_id, 'VOLATILITY', DATE '2026-01-02', 0.03,
                    'FORECAST', 'test-random-forest', 'test-1')"""
            ),
            {"security_id": security_id},
        )

    url = f"/api/v1/companies/{company.company_id}/predictions"
    response = authenticated_client.client.get(
        url, headers=authenticated_client.headers
    )
    assert response.status_code == 200, response.text
    assert {row["prediction_type"] for row in response.json()} == {"ANOMALY", "VOLATILITY"}

    filtered = authenticated_client.client.get(
        url,
        params={"prediction_type": "ANOMALY", "limit": 1},
        headers=authenticated_client.headers,
    )
    assert filtered.status_code == 200, filtered.text
    assert len(filtered.json()) == 1
    assert filtered.json()[0]["prediction_type"] == "ANOMALY"


def test_predictions_return_404_for_unknown_company(authenticated_client):
    response = authenticated_client.client.get(
        "/api/v1/companies/999999999/predictions",
        headers=authenticated_client.headers,
    )
    assert response.status_code == 404
