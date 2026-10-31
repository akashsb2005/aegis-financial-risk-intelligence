-- AEGIS integration checks for a disposable PostgreSQL test database.
-- This script writes only deterministic test fixtures into the CI database.
-- It is NOT intended to be run against a production or personal database.

DO $$
DECLARE
    v_company_id integer;
    v_assessment_id integer;
    v_audit_count integer;
    v_rejected boolean := false;
BEGIN
    INSERT INTO public.companies (company_name, industry, country)
    VALUES ('AEGIS CI Verification Company', 'Testing', 'IN')
    RETURNING company_id INTO v_company_id;

    INSERT INTO public.risk_assessment
        (company_id, risk_score, risk_level, model_version, explanation)
    VALUES
        (v_company_id, 72.50, 'HIGH', 'ci-test-1.0',
         'Automated integration-test assessment')
    RETURNING risk_assessment_id INTO v_assessment_id;

    SELECT COUNT(*) INTO v_audit_count
    FROM public.risk_assessment_audit
    WHERE risk_assessment_id = v_assessment_id
      AND company_id = v_company_id
      AND risk_score = 72.50
      AND action_type = 'INSERT';

    IF v_audit_count <> 1 THEN
        RAISE EXCEPTION 'Audit trigger check failed: expected one matching audit row, found %', v_audit_count;
    END IF;

    -- The append-only trigger must reject UPDATE.
    BEGIN
        UPDATE public.risk_assessment
        SET explanation = 'This update must be rejected'
        WHERE risk_assessment_id = v_assessment_id;
    EXCEPTION WHEN raise_exception THEN
        v_rejected := true;
    END;

    IF NOT v_rejected THEN
        RAISE EXCEPTION 'Append-only check failed: UPDATE was not rejected';
    END IF;

    -- The append-only trigger must reject DELETE.
    v_rejected := false;
    BEGIN
        DELETE FROM public.risk_assessment
        WHERE risk_assessment_id = v_assessment_id;
    EXCEPTION WHEN raise_exception THEN
        v_rejected := true;
    END;

    IF NOT v_rejected THEN
        RAISE EXCEPTION 'Append-only check failed: DELETE was not rejected';
    END IF;

    -- A score outside the documented 0..100 range must fail its CHECK.
    v_rejected := false;
    BEGIN
        INSERT INTO public.risk_assessment
            (company_id, risk_score, risk_level, model_version)
        VALUES
            (v_company_id, 150, 'CRITICAL', 'ci-invalid-score');
    EXCEPTION WHEN check_violation THEN
        v_rejected := true;
    END;

    IF NOT v_rejected THEN
        RAISE EXCEPTION 'Risk score constraint check failed: invalid score was accepted';
    END IF;

    RAISE NOTICE 'AEGIS integration checks passed: audit trigger, append-only UPDATE/DELETE protection, and risk-score CHECK constraint.';
END;
$$;
