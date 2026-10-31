-- ============================================================
-- AEGIS: Database verification and evidence queries
-- PostgreSQL 18.x
-- READ-ONLY: this file does not INSERT, UPDATE, DELETE or DROP.
-- Run after applying database/ddl/01_schema.sql.
-- ============================================================

-- 1. Confirm PostgreSQL version and current database.
SELECT version() AS postgres_version, current_database() AS database_name,
       current_user AS connected_role;

-- 2. Confirm the expected relations exist.
SELECT expected.table_name,
       CASE WHEN actual.table_name IS NULL THEN 'MISSING' ELSE 'PRESENT' END AS status
FROM (VALUES
    ('companies'),
    ('financial_records'),
    ('roles'),
    ('users'),
    ('user_sessions'),
    ('password_reset_tokens'),
    ('risk_assessment'),
    ('risk_assessment_audit')
) AS expected(table_name)
LEFT JOIN information_schema.tables AS actual
  ON actual.table_schema = 'public'
 AND actual.table_name = expected.table_name
ORDER BY expected.table_name;

-- 3. Inspect columns, data types, nullability and defaults.
SELECT table_name, ordinal_position, column_name, data_type,
       character_maximum_length, numeric_precision, numeric_scale,
       is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'companies', 'financial_records', 'roles', 'users',
      'user_sessions', 'password_reset_tokens',
      'risk_assessment', 'risk_assessment_audit'
  )
ORDER BY table_name, ordinal_position;

-- 4. Inspect primary, foreign, unique and check constraints.
SELECT tc.table_name, tc.constraint_name, tc.constraint_type,
       kcu.column_name, ccu.table_name AS referenced_table,
       ccu.column_name AS referenced_column
FROM information_schema.table_constraints AS tc
LEFT JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_schema = kcu.constraint_schema
 AND tc.constraint_name = kcu.constraint_name
 AND tc.table_name = kcu.table_name
LEFT JOIN information_schema.constraint_column_usage AS ccu
  ON tc.constraint_schema = ccu.constraint_schema
 AND tc.constraint_name = ccu.constraint_name
WHERE tc.constraint_schema = 'public'
  AND tc.table_name IN (
      'companies', 'financial_records', 'roles', 'users',
      'user_sessions', 'password_reset_tokens',
      'risk_assessment', 'risk_assessment_audit'
  )
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name, kcu.ordinal_position;

-- 5. Inspect indexes.
SELECT tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- 6. Inspect non-internal triggers.
SELECT event_object_table AS table_name, trigger_name,
       event_manipulation, action_timing, action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- 7. Inspect views and routines.
SELECT table_name AS view_name
FROM information_schema.views
WHERE table_schema = 'public'
ORDER BY table_name;

SELECT routine_name, routine_type, data_type AS return_type
FROM information_schema.routines
WHERE routine_schema = 'public'
ORDER BY routine_type, routine_name;

-- 8. Confirm extensions installed in this database.
SELECT extname, extversion
FROM pg_extension
ORDER BY extname;

-- 9. Data-volume summary. Empty tables are valid; the output records
-- what data is actually present at the time of verification.
SELECT 'companies' AS relation, COUNT(*) AS row_count FROM public.companies
UNION ALL SELECT 'financial_records', COUNT(*) FROM public.financial_records
UNION ALL SELECT 'roles', COUNT(*) FROM public.roles
UNION ALL SELECT 'users', COUNT(*) FROM public.users
UNION ALL SELECT 'user_sessions', COUNT(*) FROM public.user_sessions
UNION ALL SELECT 'password_reset_tokens', COUNT(*) FROM public.password_reset_tokens
UNION ALL SELECT 'risk_assessment', COUNT(*) FROM public.risk_assessment
UNION ALL SELECT 'risk_assessment_audit', COUNT(*) FROM public.risk_assessment_audit
ORDER BY relation;

-- 10. Risk distribution and company-level history.
SELECT risk_level, COUNT(*) AS assessment_count,
       ROUND(AVG(risk_score), 2) AS average_score,
       MIN(risk_score) AS minimum_score,
       MAX(risk_score) AS maximum_score
FROM public.risk_assessment
GROUP BY risk_level
ORDER BY risk_level;

SELECT c.company_id, c.company_name,
       COUNT(ra.risk_assessment_id) AS assessment_count,
       MAX(ra.assessed_at) AS latest_assessment_at
FROM public.companies AS c
LEFT JOIN public.risk_assessment AS ra
  ON ra.company_id = c.company_id
GROUP BY c.company_id, c.company_name
ORDER BY c.company_name;

-- End of read-only verification script.
