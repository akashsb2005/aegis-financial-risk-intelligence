-- Fail-fast checks for the market/evidence foundation migration.
DO $$
DECLARE
  required_table TEXT;
BEGIN
  FOREACH required_table IN ARRAY ARRAY[
    'securities', 'market_observations', 'financial_events',
    'news_articles', 'model_predictions'
  ] LOOP
    IF to_regclass('public.' || required_table) IS NULL THEN
      RAISE EXCEPTION 'Missing required table: %', required_table;
    END IF;
  END LOOP;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'public.market_observations'::regclass
      AND conname = 'uq_market_observation'
  ) THEN
    RAISE EXCEPTION 'Missing market observation uniqueness constraint';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'public.securities'::regclass
      AND conname = 'uq_securities_exchange_ticker'
  ) THEN
    RAISE EXCEPTION 'Missing exchange/ticker uniqueness constraint';
  END IF;
END $$;

-- Confirm seed mappings without assuming generated company/security IDs.
SELECT s.ticker, s.exchange, c.company_name, s.currency
FROM public.securities s
JOIN public.companies c USING (company_id)
ORDER BY s.exchange, s.ticker;
