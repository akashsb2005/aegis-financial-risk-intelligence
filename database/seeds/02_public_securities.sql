-- Public-company/security master for market-data demonstrations.
-- Contains identifiers only; no market prices or financial statements are fabricated.
BEGIN;

INSERT INTO public.companies (company_name, industry, country)
SELECT v.company_name, v.industry, v.country
FROM (VALUES
  ('Apple Inc.', 'Technology', 'United States'),
  ('Microsoft Corporation', 'Technology', 'United States'),
  ('NVIDIA Corporation', 'Semiconductors', 'United States'),
  ('Tata Consultancy Services Limited', 'Information Technology', 'India'),
  ('Reliance Industries Limited', 'Conglomerates', 'India')
) AS v(company_name, industry, country)
WHERE NOT EXISTS (
  SELECT 1 FROM public.companies c WHERE c.company_name = v.company_name
);

INSERT INTO public.securities (company_id, ticker, exchange, asset_type, currency)
SELECT c.company_id, v.ticker, v.exchange, 'EQUITY', v.currency
FROM (VALUES
  ('Apple Inc.', 'AAPL', 'NASDAQ', 'USD'),
  ('Microsoft Corporation', 'MSFT', 'NASDAQ', 'USD'),
  ('NVIDIA Corporation', 'NVDA', 'NASDAQ', 'USD'),
  ('Tata Consultancy Services Limited', 'TCS.NS', 'NSE', 'INR'),
  ('Reliance Industries Limited', 'RELIANCE.NS', 'NSE', 'INR')
) AS v(company_name, ticker, exchange, currency)
JOIN public.companies c ON c.company_name = v.company_name
ON CONFLICT (exchange, ticker) DO NOTHING;

COMMIT;
