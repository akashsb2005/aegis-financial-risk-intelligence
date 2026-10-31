-- AEGIS transaction demonstrations for a disposable PostgreSQL test database.
-- Demonstrates COMMIT, SAVEPOINT/ROLLBACK TO SAVEPOINT, and full ROLLBACK.
-- Uses unique, deterministic registration numbers and synthetic records only.
-- Run with psql; the workflow uses ON_ERROR_STOP=1.

-- 1. COMMIT: both related writes become durable together.
BEGIN;

INSERT INTO public.companies
    (company_name, registration_number, industry, country)
VALUES
    ('AEGIS Transaction Commit CI', 'AEGIS-TX-COMMIT-CI', 'Testing', 'IN')
RETURNING company_id AS tx_commit_company_id \gset

INSERT INTO public.financial_records
    (company_id, fiscal_year, revenue, net_profit)
VALUES
    (:tx_commit_company_id, 2025, 100000.00, 12000.00);

COMMIT;

DO $$
DECLARE
    v_company_id integer;
    v_record_count integer;
BEGIN
    SELECT company_id INTO v_company_id
    FROM public.companies
    WHERE registration_number = 'AEGIS-TX-COMMIT-CI';

    SELECT COUNT(*) INTO v_record_count
    FROM public.financial_records
    WHERE company_id = v_company_id AND fiscal_year = 2025;

    IF v_company_id IS NULL OR v_record_count <> 1 THEN
        RAISE EXCEPTION 'COMMIT check failed: expected company and its financial record';
    END IF;
END;
$$;

-- 2. SAVEPOINT: retain the company, but undo only the optional financial row.
BEGIN;

INSERT INTO public.companies
    (company_name, registration_number, industry, country)
VALUES
    ('AEGIS Savepoint CI', 'AEGIS-TX-SAVEPOINT-CI', 'Testing', 'IN')
RETURNING company_id AS tx_savepoint_company_id \gset

SAVEPOINT before_optional_financial_record;

INSERT INTO public.financial_records
    (company_id, fiscal_year, revenue, net_profit)
VALUES
    (:tx_savepoint_company_id, 2025, 50000.00, 4000.00);

ROLLBACK TO SAVEPOINT before_optional_financial_record;
COMMIT;

DO $$
DECLARE
    v_company_id integer;
    v_record_count integer;
BEGIN
    SELECT company_id INTO v_company_id
    FROM public.companies
    WHERE registration_number = 'AEGIS-TX-SAVEPOINT-CI';

    SELECT COUNT(*) INTO v_record_count
    FROM public.financial_records
    WHERE company_id = v_company_id AND fiscal_year = 2025;

    IF v_company_id IS NULL OR v_record_count <> 0 THEN
        RAISE EXCEPTION 'SAVEPOINT check failed: company should remain and optional record should be rolled back';
    END IF;
END;
$$;

-- 3. Full ROLLBACK: neither related write should remain.
BEGIN;

INSERT INTO public.companies
    (company_name, registration_number, industry, country)
VALUES
    ('AEGIS Full Rollback CI', 'AEGIS-TX-ROLLBACK-CI', 'Testing', 'IN')
RETURNING company_id AS tx_rollback_company_id \gset

INSERT INTO public.financial_records
    (company_id, fiscal_year, revenue, net_profit)
VALUES
    (:tx_rollback_company_id, 2025, 25000.00, 1500.00);

ROLLBACK;

DO $$
DECLARE
    v_company_count integer;
    v_record_count integer;
BEGIN
    SELECT COUNT(*) INTO v_company_count
    FROM public.companies
    WHERE registration_number = 'AEGIS-TX-ROLLBACK-CI';

    SELECT COUNT(*) INTO v_record_count
    FROM public.financial_records fr
    JOIN public.companies c ON c.company_id = fr.company_id
    WHERE c.registration_number = 'AEGIS-TX-ROLLBACK-CI';

    IF v_company_count <> 0 OR v_record_count <> 0 THEN
        RAISE EXCEPTION 'ROLLBACK check failed: transaction writes were not fully undone';
    END IF;
END;
$$;

\echo 'AEGIS transaction checks passed: COMMIT, SAVEPOINT rollback, and full ROLLBACK.'
