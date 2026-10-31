-- AEGIS deterministic demo dataset
-- Safe to execute repeatedly. Uses synthetic, non-personal demonstration data.
BEGIN;

INSERT INTO public.roles (role_name, description)
VALUES
  ('ADMIN', 'Administrative access for project demonstration'),
  ('ANALYST', 'Reviews company financial data and risk assessments')
ON CONFLICT (role_name) DO NOTHING;

INSERT INTO public.companies
  (company_name, registration_number, industry, country, annual_revenue, employee_count)
VALUES
  ('Aster Manufacturing Ltd', 'AEGIS-DEMO-001', 'Manufacturing', 'India', 185000000.00, 840),
  ('BluePeak Fintech Ltd', 'AEGIS-DEMO-002', 'Financial Services', 'India', 92000000.00, 310),
  ('Cedar Energy Systems Ltd', 'AEGIS-DEMO-003', 'Energy', 'India', 247000000.00, 1250)
ON CONFLICT (registration_number) DO NOTHING;

INSERT INTO public.users (role_id, full_name, email, password_hash)
SELECT r.role_id, 'AEGIS Demo Analyst', 'demo.analyst@aegis.example',
       crypt('Demo-Only-Password-Not-For-Production', gen_salt('bf'))
FROM public.roles r
WHERE r.role_name = 'ANALYST'
ON CONFLICT (email) DO NOTHING;

INSERT INTO public.financial_records
  (company_id, fiscal_year, revenue, net_profit, total_assets, total_liabilities,
   total_debt, shareholders_equity, operating_cash_flow)
SELECT c.company_id, v.fiscal_year, v.revenue, v.net_profit, v.total_assets,
       v.total_liabilities, v.total_debt, v.shareholders_equity, v.operating_cash_flow
FROM (VALUES
  ('AEGIS-DEMO-001', 2024, 178000000.00, 16200000.00, 221000000.00, 94000000.00, 51000000.00, 127000000.00, 18800000.00),
  ('AEGIS-DEMO-001', 2025, 185000000.00, 14100000.00, 236000000.00, 113000000.00, 68000000.00, 123000000.00, 15100000.00),
  ('AEGIS-DEMO-002', 2024, 81000000.00, 9800000.00, 119000000.00, 73000000.00, 42000000.00, 46000000.00, 11200000.00),
  ('AEGIS-DEMO-002', 2025, 92000000.00, 7400000.00, 132000000.00, 91000000.00, 59000000.00, 41000000.00, 8300000.00),
  ('AEGIS-DEMO-003', 2024, 226000000.00, 23100000.00, 310000000.00, 141000000.00, 87000000.00, 169000000.00, 26000000.00),
  ('AEGIS-DEMO-003', 2025, 247000000.00, 27800000.00, 344000000.00, 149000000.00, 91000000.00, 195000000.00, 31200000.00)
) AS v(registration_number, fiscal_year, revenue, net_profit, total_assets, total_liabilities, total_debt, shareholders_equity, operating_cash_flow)
JOIN public.companies c ON c.registration_number = v.registration_number
ON CONFLICT (company_id, fiscal_year) DO NOTHING;

-- Insert one initial risk assessment per demo company. The audit trigger
-- automatically writes the corresponding audit snapshot.
INSERT INTO public.risk_assessment
  (company_id, risk_score, risk_level, model_version, explanation, assessed_by)
SELECT c.company_id, v.risk_score, v.risk_level, 'demo-rules-v1',
       v.explanation, u.user_id
FROM (VALUES
  ('AEGIS-DEMO-001', 42.50::numeric, 'MEDIUM', 'Synthetic demonstration assessment: moderate leverage and stable operating cash flow.'),
  ('AEGIS-DEMO-002', 78.00::numeric, 'HIGH', 'Synthetic demonstration assessment: elevated liabilities relative to assets and reduced cash-flow coverage.'),
  ('AEGIS-DEMO-003', 24.00::numeric, 'LOW', 'Synthetic demonstration assessment: improving profitability and positive operating cash flow.')
) AS v(registration_number, risk_score, risk_level, explanation)
JOIN public.companies c ON c.registration_number = v.registration_number
CROSS JOIN public.users u
WHERE u.email = 'demo.analyst@aegis.example'
  AND NOT EXISTS (
    SELECT 1 FROM public.risk_assessment ra WHERE ra.company_id = c.company_id
  );

COMMIT;
