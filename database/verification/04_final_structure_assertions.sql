-- Fail-fast structural assertions for the AEGIS PostgreSQL schema.
DO $$
DECLARE
 expected_tables text[] := ARRAY['companies','financial_records','roles','users','user_sessions','password_reset_tokens','risk_assessment','risk_assessment_audit'];
 table_name text; missing text[] := ARRAY[]::text[]; object_count integer;
BEGIN
 FOREACH table_name IN ARRAY expected_tables LOOP
  IF to_regclass(format('public.%I',table_name)) IS NULL THEN missing:=array_append(missing,table_name); END IF;
 END LOOP;
 IF cardinality(missing)>0 THEN RAISE EXCEPTION 'Missing tables: %',array_to_string(missing,', '); END IF;
 SELECT COUNT(*) INTO object_count FROM pg_constraint WHERE connamespace='public'::regnamespace AND contype IN ('p','f','u','c');
 IF object_count<20 THEN RAISE EXCEPTION 'Expected at least 20 integrity constraints; found %',object_count; END IF;
 SELECT COUNT(*) INTO object_count FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND NOT t.tgisinternal;
 IF object_count<2 THEN RAISE EXCEPTION 'Expected both risk-assessment triggers; found %',object_count; END IF;
 IF to_regclass('public.company_risk_view') IS NULL THEN RAISE EXCEPTION 'company_risk_view missing'; END IF;
 IF to_regprocedure('public.compute_risk_delta(integer,integer)') IS NULL
 OR to_regprocedure('public.get_company_risk_level(integer)') IS NULL
 OR to_regprocedure('public.add_risk_assessment(integer,numeric,character varying,character varying,text,integer)') IS NULL
 THEN RAISE EXCEPTION 'One or more required routines are missing'; END IF;
 IF NOT EXISTS(SELECT 1 FROM pg_indexes WHERE schemaname='public' AND indexname='idx_risk_assessment_company_date')
 THEN RAISE EXCEPTION 'Required risk lookup index is missing'; END IF;
 RAISE NOTICE 'AEGIS structural assertions passed: 8 tables, integrity constraints, triggers, view, routines, and index.';
END;
$$;
