from uuid import uuid4

import pytest
from sqlalchemy import text

from app.core.database import engine


@pytest.fixture
def market_data(company):
    unique_id = uuid4().hex
    with engine.begin() as connection:
        company_b_id = connection.execute(
            text(
                """
                INSERT INTO public.companies
                    (company_name, registration_number, industry, country,
                     annual_revenue, employee_count)
                VALUES
                    (:name, :registration, 'Testing', 'IN', 1000, 5)
                RETURNING company_id
                """
            ),
            {
                "name": f"Market API Test B {unique_id[:12]}",
                "registration": f"AEGIS-MARKET-TEST-{unique_id}",
            },
        ).scalar_one()

        security_a_id = connection.execute(
            text(
                """
                INSERT INTO public.securities
                    (company_id, ticker, exchange, currency)
                VALUES (:company_id, :ticker, 'TEST', 'USD')
                RETURNING security_id
                """
            ),
            {
                "company_id": company.company_id,
                "ticker": f"TESTA{unique_id[:8]}",
            },
        ).scalar_one()
        inactive_security_a_id = connection.execute(
            text(
                """
                INSERT INTO public.securities
                    (company_id, ticker, exchange, currency, is_active)
                VALUES (:company_id, :ticker, 'TEST', 'USD', FALSE)
                RETURNING security_id
                """
            ),
            {
                "company_id": company.company_id,
                "ticker": f"TESTAI{unique_id[:7]}",
            },
        ).scalar_one()
        security_b_id = connection.execute(
            text(
                """
                INSERT INTO public.securities
                    (company_id, ticker, exchange, currency)
                VALUES (:company_id, :ticker, 'TEST', 'USD')
                RETURNING security_id
                """
            ),
            {
                "company_id": company_b_id,
                "ticker": f"TESTB{unique_id[:8]}",
            },
        ).scalar_one()

        connection.execute(
            text(
                """
                INSERT INTO public.market_observations
                    (security_id, observation_date, open, high, low, close,
                     adjusted_close, volume, source)
                VALUES
                    (:security_a, '2026-01-01', 10, 12, 9, 11, 11, 100, 'fixture'),
                    (:security_a, '2026-01-02', 11, 13, 10, 12, 12, 200, 'fixture'),
                    (:security_a, '2026-01-03', 12, 14, 11, 13, 13, 300, 'fixture'),
                    (:security_b, '2026-01-02', 20, 22, 19, 21, 21, 400, 'fixture')
                """
            ),
            {"security_a": security_a_id, "security_b": security_b_id},
        )

        connection.execute(
            text(
                """
                INSERT INTO public.financial_events
                    (company_id, event_type, event_date, title, description,
                     source_name, source_uri, published_at)
                VALUES
                    (:company_a, 'EARNINGS', '2026-01-02', 'A earnings', 'Results',
                     'Test source', :source_a, '2026-01-02T10:00:00Z'),
                    (:company_a, 'MERGER', '2026-01-03', 'A merger', NULL,
                     NULL, :source_b, NULL),
                    (:company_b, 'EARNINGS', '2026-01-02', 'B earnings', NULL,
                     'Test source', :source_c, NULL)
                """
            ),
            {
                "company_a": company.company_id,
                "company_b": company_b_id,
                "source_a": f"https://tests.invalid/{unique_id}/event-a",
                "source_b": f"https://tests.invalid/{unique_id}/event-a2",
                "source_c": f"https://tests.invalid/{unique_id}/event-b",
            },
        )

        connection.execute(
            text(
                """
                INSERT INTO public.news_articles
                    (company_id, security_id, title, content, source_name,
                     source_uri, published_at)
                VALUES
                    (:company_a, NULL, 'A direct article', 'Direct content',
                     'Test source', :article_a, '2026-01-02T08:00:00Z'),
                    (NULL, :security_a, 'A security article', 'Security content',
                     'Test source', :article_a_security, '2026-01-03T08:00:00Z'),
                    (:company_b, NULL, 'B direct article', 'Other content',
                     'Test source', :article_b, '2026-01-02T08:00:00Z'),
                    (NULL, :security_b, 'B security article', 'Other security content',
                     'Test source', :article_b_security, '2026-01-03T08:00:00Z'),
                    (:company_a, NULL, 'A undated article', 'No publication date',
                     'Test source', :article_a_undated, NULL)
                """
            ),
            {
                "company_a": company.company_id,
                "company_b": company_b_id,
                "security_a": security_a_id,
                "security_b": security_b_id,
                "article_a": f"https://tests.invalid/{unique_id}/article-a",
                "article_a_security": f"https://tests.invalid/{unique_id}/article-a-security",
                "article_b": f"https://tests.invalid/{unique_id}/article-b",
                "article_b_security": f"https://tests.invalid/{unique_id}/article-b-security",
                "article_a_undated": f"https://tests.invalid/{unique_id}/article-a-undated",
            },
        )

    return {
        "company_a_id": company.company_id,
        "company_b_id": company_b_id,
        "security_a_id": security_a_id,
        "inactive_security_a_id": inactive_security_a_id,
        "security_b_id": security_b_id,
    }


def test_company_securities_are_authenticated_and_return_schema(
    authenticated_client,
    market_data,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{market_data['company_a_id']}/securities",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    securities = response.json()
    assert len(securities) == 1
    assert set(securities[0]) == {
        "security_id",
        "company_id",
        "ticker",
        "exchange",
        "asset_type",
        "currency",
        "is_active",
        "created_at",
    }
    assert securities[0]["security_id"] == market_data["security_a_id"]
    assert securities[0]["company_id"] == market_data["company_a_id"]

    all_securities = authenticated_client.client.get(
        f"/api/v1/companies/{market_data['company_a_id']}/securities?active_only=false",
        headers=authenticated_client.headers,
    )
    assert all_securities.status_code == 200
    assert {row["security_id"] for row in all_securities.json()} == {
        market_data["security_a_id"],
        market_data["inactive_security_a_id"],
    }


@pytest.mark.parametrize(
    "path_suffix",
    [
        "securities",
        "market-observations",
        "events",
        "news",
    ],
)
def test_market_reads_require_authentication(client, company, path_suffix):
    response = client.get(
        f"/api/v1/companies/{company.company_id}/{path_suffix}"
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


@pytest.mark.parametrize(
    "path_suffix",
    [
        "securities",
        "market-observations",
        "events",
        "news",
    ],
)
def test_market_reads_return_not_found_for_missing_company(
    authenticated_client,
    path_suffix,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/2147483647/{path_suffix}",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "COMPANY_NOT_FOUND"


def test_company_securities_do_not_leak_between_companies(
    authenticated_client,
    market_data,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{market_data['company_a_id']}/securities",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    assert all(
        row["company_id"] == market_data["company_a_id"]
        for row in response.json()
    )


def test_market_observations_are_company_scoped_and_have_expected_fields(
    authenticated_client,
    market_data,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{market_data['company_a_id']}/market-observations",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    observations = response.json()
    assert len(observations) == 3
    assert all(
        row["security_id"] == market_data["security_a_id"]
        for row in observations
    )
    assert set(observations[0]) == {
        "observation_id",
        "security_id",
        "ticker",
        "exchange",
        "observation_date",
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "volume",
        "source",
        "ingested_at",
    }
    assert observations[0]["observation_date"] == "2026-01-03"
    assert observations[0]["close"] == "13.000000"


@pytest.mark.parametrize("path_suffix", ["market-observations", "news"])
def test_other_company_security_is_not_visible(
    authenticated_client,
    market_data,
    path_suffix,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{market_data['company_a_id']}/{path_suffix}"
        f"?security_id={market_data['security_b_id']}",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SECURITY_NOT_FOUND"


def test_market_observation_date_filters_and_pagination(
    authenticated_client,
    market_data,
):
    base_url = (
        f"/api/v1/companies/{market_data['company_a_id']}/market-observations"
    )
    filtered = authenticated_client.client.get(
        f"{base_url}?start_date=2026-01-02&end_date=2026-01-03",
        headers=authenticated_client.headers,
    )
    assert filtered.status_code == 200
    assert [row["observation_date"] for row in filtered.json()] == [
        "2026-01-03",
        "2026-01-02",
    ]

    page = authenticated_client.client.get(
        f"{base_url}?limit=1&offset=1",
        headers=authenticated_client.headers,
    )
    assert page.status_code == 200
    assert len(page.json()) == 1
    assert page.json()[0]["observation_date"] == "2026-01-02"

    invalid_range = authenticated_client.client.get(
        f"{base_url}?start_date=2026-01-03&end_date=2026-01-02",
        headers=authenticated_client.headers,
    )
    assert invalid_range.status_code == 422


def test_company_without_market_observations_returns_empty_list(
    authenticated_client,
    company,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{company.company_id}/market-observations",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_events_are_company_scoped_and_return_expected_fields(
    authenticated_client,
    market_data,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{market_data['company_a_id']}/events",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    events = response.json()
    assert len(events) == 2
    assert all(row["company_id"] == market_data["company_a_id"] for row in events)
    assert events[0]["title"] == "A merger"
    assert set(events[0]) == {
        "event_id",
        "company_id",
        "event_type",
        "event_date",
        "title",
        "description",
        "source_name",
        "source_uri",
        "published_at",
        "created_at",
    }


def test_event_type_and_date_filters(authenticated_client, market_data):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{market_data['company_a_id']}/events"
        "?event_type=EARNINGS&start_date=2026-01-02&end_date=2026-01-02",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "A earnings"


def test_company_without_events_returns_empty_list(authenticated_client, company):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{company.company_id}/events",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_news_includes_direct_and_company_security_articles_without_leaks(
    authenticated_client,
    market_data,
):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{market_data['company_a_id']}/news",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    articles = response.json()
    assert {row["title"] for row in articles} == {
        "A direct article",
        "A security article",
        "A undated article",
    }
    assert articles[0]["title"] == "A security article"
    assert articles[-1]["title"] == "A undated article"
    assert set(articles[0]) == {
        "article_id",
        "company_id",
        "security_id",
        "title",
        "content",
        "source_name",
        "source_uri",
        "published_at",
        "ingested_at",
    }


def test_news_security_and_published_date_filters(authenticated_client, market_data):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{market_data['company_a_id']}/news"
        f"?security_id={market_data['security_a_id']}"
        "&start_date=2026-01-03&end_date=2026-01-03",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "A security article"


def test_company_without_news_returns_empty_list(authenticated_client, company):
    response = authenticated_client.client.get(
        f"/api/v1/companies/{company.company_id}/news",
        headers=authenticated_client.headers,
    )

    assert response.status_code == 200
    assert response.json() == []
