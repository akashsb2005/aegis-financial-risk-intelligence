"""Shared fixtures for API tests against a disposable PostgreSQL database."""

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from starlette.testclient import TestClient


_test_database_url = os.environ.get("AEGIS_TEST_DATABASE_URL", "").strip()
if not _test_database_url:
    raise RuntimeError(
        "API tests require AEGIS_TEST_DATABASE_URL pointing to a disposable "
        "PostgreSQL database whose name contains 'test'. No application database "
        "fallback is allowed."
    )

try:
    _parsed_test_database_url = make_url(_test_database_url)
except ArgumentError as error:
    raise RuntimeError("AEGIS_TEST_DATABASE_URL is not a valid SQLAlchemy URL.") from error

if _parsed_test_database_url.get_backend_name() != "postgresql":
    raise RuntimeError("API tests require PostgreSQL; SQLite and other backends are unsupported.")
if not _parsed_test_database_url.database or not re.search(
    r"(?:^|[_-])test(?:$|[_-])",
    _parsed_test_database_url.database,
    re.IGNORECASE,
):
    raise RuntimeError(
        "AEGIS_TEST_DATABASE_URL must target a database with 'test' as a delimited "
        "name component (for example, aegis_test)."
    )

_application_database_url = os.environ.get("AEGIS_DATABASE_URL", "").strip()
if _application_database_url and _application_database_url == _test_database_url:
    raise RuntimeError(
        "AEGIS_TEST_DATABASE_URL must be separate from AEGIS_DATABASE_URL."
    )

os.environ["AEGIS_DATABASE_URL"] = _test_database_url
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import create_app  # noqa: E402


@dataclass(frozen=True)
class AccountData:
    full_name: str
    email: str
    password: str


@dataclass(frozen=True)
class AuthenticatedSession:
    client: TestClient
    headers: dict[str, str]
    user_id: int


@dataclass(frozen=True)
class CompanyData:
    company_id: int
    registration_number: str


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Provide an API client backed by the explicitly configured test database."""
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def account_data() -> AccountData:
    unique_id = uuid4().hex
    return AccountData(
        full_name=f"AEGIS API Test {unique_id[:12]}",
        email=f"api-test-{unique_id}@tests.aegis.invalid",
        password=f"Test-Password-{unique_id[:16]}",
    )


@pytest.fixture
def registered_account(client: TestClient, account_data: AccountData) -> AccountData:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": account_data.full_name,
            "email": account_data.email,
            "password": account_data.password,
        },
    )
    assert response.status_code == 201, response.text
    return account_data


@pytest.fixture
def authenticated_client(
    client: TestClient,
    registered_account: AccountData,
) -> AuthenticatedSession:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_account.email,
            "password": registered_account.password,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    return AuthenticatedSession(
        client=client,
        headers={"Authorization": f"Bearer {body['access_token']}"},
        user_id=body["user"]["user_id"],
    )


@pytest.fixture
def company() -> CompanyData:
    unique_id = uuid4().hex
    registration_number = f"AEGIS-API-TEST-{unique_id}"
    with engine.begin() as connection:
        company_id = connection.execute(
            text(
                """
                INSERT INTO public.companies
                    (company_name, registration_number, industry, country,
                     annual_revenue, employee_count)
                VALUES
                    (:company_name, :registration_number, 'Testing', 'IN',
                     12345.67, 10)
                RETURNING company_id
                """
            ),
            {
                "company_name": f"AEGIS API Test {unique_id[:12]}",
                "registration_number": registration_number,
            },
        ).scalar_one()
    return CompanyData(company_id=company_id, registration_number=registration_number)


@pytest.fixture
def insert_financial_record():
    def insert_record(
        company_id: int,
        fiscal_year: int,
        revenue: str,
    ) -> None:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO public.financial_records
                        (company_id, fiscal_year, revenue, net_profit, total_assets,
                         total_liabilities, total_debt, shareholders_equity,
                         operating_cash_flow)
                    VALUES
                        (:company_id, :fiscal_year, :revenue, 120.00, 2000.00,
                         800.00, 300.00, 1200.00, 100.00)
                    """
                ),
                {
                    "company_id": company_id,
                    "fiscal_year": fiscal_year,
                    "revenue": revenue,
                },
            )

    return insert_record


@pytest.fixture
def admin_authenticated_client(
    client: TestClient,
) -> AuthenticatedSession:
    unique_id = uuid4().hex
    email = f"admin-test-{unique_id}@tests.aegis.invalid"
    password = f"Test-Password-{unique_id[:16]}"
    with engine.begin() as connection:
        user_id = connection.execute(
            text(
                """
                INSERT INTO public.users (role_id, full_name, email, password_hash)
                SELECT role_id, :full_name, :email, :password_hash
                FROM public.roles
                WHERE role_name = 'ADMIN'
                RETURNING user_id
                """
            ),
            {
                "full_name": f"AEGIS Admin Test {unique_id[:12]}",
                "email": email,
                "password_hash": hash_password(password),
            },
        ).scalar_one()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return AuthenticatedSession(
        client=client,
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
        user_id=user_id,
    )
