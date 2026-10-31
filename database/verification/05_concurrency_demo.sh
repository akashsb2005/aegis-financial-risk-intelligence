#!/usr/bin/env bash
set -euo pipefail
REGISTRATION='AEGIS-CONCURRENCY-CI'
COMPANY_ID="$(psql -X -qAt -v ON_ERROR_STOP=1 -c "
 INSERT INTO public.companies(company_name,registration_number,industry,country)
 VALUES ('AEGIS Concurrency CI','AEGIS-CONCURRENCY-CI','Testing','IN')
 ON CONFLICT(registration_number) DO UPDATE SET company_name=EXCLUDED.company_name
 RETURNING company_id;
" | tail -n 1)"
cleanup() {
 [[ -n "${LOCK_PID:-}" ]] && kill "$LOCK_PID" 2>/dev/null || true
 [[ -n "${SNAPSHOT_PID:-}" ]] && kill "$SNAPSHOT_PID" 2>/dev/null || true
 psql -X -v ON_ERROR_STOP=1 -c "DELETE FROM public.companies WHERE company_id=${COMPANY_ID};" >/dev/null || true
}
trap cleanup EXIT
psql -X -v ON_ERROR_STOP=1 -v company_id="$COMPANY_ID" <<'SQL'
INSERT INTO public.financial_records(company_id,fiscal_year,revenue,net_profit)
VALUES (:company_id,2025,100000.00,10000.00)
ON CONFLICT(company_id,fiscal_year) DO UPDATE
SET revenue=EXCLUDED.revenue,net_profit=EXCLUDED.net_profit;
SQL
LOCK_LOG="$(mktemp)"
psql -X -v ON_ERROR_STOP=1 -v company_id="$COMPANY_ID" >"$LOCK_LOG" 2>&1 <<'SQL' &
BEGIN;
SELECT financial_record_id FROM public.financial_records
WHERE company_id=:company_id AND fiscal_year=2025 FOR UPDATE;
\echo ROW_LOCK_HELD
SELECT pg_sleep(4);
COMMIT;
SQL
LOCK_PID=$!
for _ in $(seq 1 100); do
 grep -q ROW_LOCK_HELD "$LOCK_LOG" && break
 kill -0 "$LOCK_PID" 2>/dev/null || { cat "$LOCK_LOG"; exit 1; }
 sleep 0.1
done
grep -q ROW_LOCK_HELD "$LOCK_LOG" || { cat "$LOCK_LOG"; echo 'Timed out waiting for row lock'; exit 1; }
LOCK_START="$(date +%s)"
psql -X -v ON_ERROR_STOP=1 -v company_id="$COMPANY_ID" <<'SQL'
BEGIN;
SELECT financial_record_id FROM public.financial_records
WHERE company_id=:company_id AND fiscal_year=2025 FOR UPDATE;
UPDATE public.financial_records SET revenue=revenue+1000
WHERE company_id=:company_id AND fiscal_year=2025;
COMMIT;
SQL
LOCK_ELAPSED=$(( $(date +%s)-LOCK_START ))
wait "$LOCK_PID"; unset LOCK_PID; rm -f "$LOCK_LOG"
if (( LOCK_ELAPSED < 2 )); then
 echo "Expected lock wait >=2s; elapsed=${LOCK_ELAPSED}s"; exit 1
fi
echo "PASS: competing SELECT FOR UPDATE waited ${LOCK_ELAPSED}s for row lock."
SNAPSHOT_LOG="$(mktemp)"
psql -X -v ON_ERROR_STOP=1 -v company_id="$COMPANY_ID" >"$SNAPSHOT_LOG" 2>&1 <<'SQL' &
BEGIN ISOLATION LEVEL REPEATABLE READ;
CREATE TEMP TABLE aegis_snapshot AS
SELECT revenue FROM public.financial_records
WHERE company_id=:company_id AND fiscal_year=2025;
\echo REPEATABLE_READ_SNAPSHOT_READY
SELECT pg_sleep(4);
SELECT 1 / CASE WHEN
  (SELECT revenue FROM aegis_snapshot) =
  (SELECT fr.revenue FROM public.financial_records fr
   JOIN public.companies co USING (company_id)
   WHERE co.registration_number = 'AEGIS-CONCURRENCY-CI' AND fiscal_year = 2025)
THEN 1 ELSE 0 END;
COMMIT;
SQL
SNAPSHOT_PID=$!
for _ in $(seq 1 100); do
 grep -q REPEATABLE_READ_SNAPSHOT_READY "$SNAPSHOT_LOG" && break
 kill -0 "$SNAPSHOT_PID" 2>/dev/null || { cat "$SNAPSHOT_LOG"; exit 1; }
 sleep 0.1
done
grep -q REPEATABLE_READ_SNAPSHOT_READY "$SNAPSHOT_LOG" || { cat "$SNAPSHOT_LOG"; echo 'Timed out waiting for snapshot'; exit 1; }
psql -X -v ON_ERROR_STOP=1 -v company_id="$COMPANY_ID" <<'SQL'
UPDATE public.financial_records SET revenue=revenue+500
WHERE company_id=:company_id AND fiscal_year=2025;
SQL
wait "$SNAPSHOT_PID" || { cat "$SNAPSHOT_LOG"; exit 1; }
unset SNAPSHOT_PID; rm -f "$SNAPSHOT_LOG"
echo 'PASS: REPEATABLE READ retained its original snapshot during a concurrent commit.'
psql -X -v ON_ERROR_STOP=1 -v company_id="$COMPANY_ID" <<'SQL'
SELECT 1 / CASE WHEN
  (SELECT revenue FROM public.financial_records fr
   JOIN public.companies co USING (company_id)
   WHERE co.registration_number = 'AEGIS-CONCURRENCY-CI' AND fiscal_year = 2025) = 101500.00
THEN 1 ELSE 0 END;
\echo 'AEGIS concurrency checks passed: row locks, SELECT FOR UPDATE, REPEATABLE READ.'
SQL
