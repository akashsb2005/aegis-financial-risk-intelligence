
-- ============================================================
-- AEGIS: AI-Powered Financial Risk & Event Intelligence
-- File: 01_basic_queries.sql
-- Purpose: Basic SELECT, filtering, sorting, and NULL handling
-- Database: PostgreSQL
-- ============================================================


-- Q1. List all companies.
SELECT
    company_id,
    company_name,
    industry,
    country
FROM public.companies
ORDER BY company_name;


-- Q2. List companies with their financial summaries.
SELECT
    company_id,
    company_name,
    annual_revenue,
    employee_count
FROM public.companies
ORDER BY annual_revenue DESC NULLS LAST;


-- Q3. Find companies in the Financial Services industry.
SELECT
    company_id,
    company_name,
    industry,
    country
FROM public.companies
WHERE industry = 'Financial Services'
ORDER BY company_name;


-- Q4. Find companies whose annual revenue is at least 100 million.
SELECT
    company_id,
    company_name,
    annual_revenue
FROM public.companies
WHERE annual_revenue >= 100000000
ORDER BY annual_revenue DESC;


-- Q5. Find companies with missing industry information.
SELECT
    company_id,
    company_name
FROM public.companies
WHERE industry IS NULL
ORDER BY company_name;


-- Q6. List financial records for a particular fiscal year.
-- Replace 2025 with a year present in your database.
SELECT
    financial_record_id,
    company_id,
    fiscal_year,
    revenue,
    net_profit,
    total_assets,
    total_liabilities,
    total_debt,
    shareholders_equity,
    operating_cash_flow
FROM public.financial_records
WHERE fiscal_year = 2025
ORDER BY company_id;


-- Q7. Show the 10 most recent risk assessments.
SELECT
    risk_assessment_id,
    company_id,
    risk_score,
    risk_level,
    assessed_at,
    model_version
FROM public.risk_assessment
ORDER BY assessed_at DESC
LIMIT 10;


-- Q8. Find high or critical risk assessments.
SELECT
    risk_assessment_id,
    company_id,
    risk_score,
    risk_level,
    assessed_at
FROM public.risk_assessment
WHERE risk_level IN ('HIGH', 'CRITICAL')
ORDER BY risk_score DESC, assessed_at DESC;


-- Q9. Find assessments within a score range (40 to 70).
SELECT
    risk_assessment_id,
    company_id,
    risk_score,
    risk_level
FROM public.risk_assessment
WHERE risk_score BETWEEN 40 AND 70
ORDER BY risk_score DESC;


-- Q10. Count risk assessments by risk level.
SELECT
    risk_level,
    COUNT(*) AS assessment_count
FROM public.risk_assessment
GROUP BY risk_level
ORDER BY assessment_count DESC, risk_level;


-- Q11. Find the latest assessment timestamp for each company.
SELECT
    company_id,
    MAX(assessed_at) AS latest_assessment_at
FROM public.risk_assessment
GROUP BY company_id
ORDER BY company_id;


-- Q12. Show the company risk view.
SELECT *
FROM public.company_risk_view
ORDER BY assessed_at DESC
LIMIT 20;
