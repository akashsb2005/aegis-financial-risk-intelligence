
-- ============================================================
-- AEGIS: AI-Powered Financial Risk & Event Intelligence
-- File: 02_joins_and_aggregations.sql
-- Purpose: JOINs, aggregate functions, GROUP BY, and HAVING
-- Database: PostgreSQL
-- ============================================================


-- Q1. List risk assessments with their associated company details.
-- INNER JOIN returns only assessments with a matching company.
SELECT
    ra.risk_assessment_id,
    c.company_name,
    c.industry,
    c.country,
    ra.risk_score,
    ra.risk_level,
    ra.assessed_at
FROM public.risk_assessment AS ra
INNER JOIN public.companies AS c
    ON ra.company_id = c.company_id
ORDER BY ra.assessed_at DESC;


-- Q2. List every company, including companies without risk assessments.
-- LEFT JOIN preserves all companies.
SELECT
    c.company_id,
    c.company_name,
    ra.risk_assessment_id,
    ra.risk_score,
    ra.risk_level
FROM public.companies AS c
LEFT JOIN public.risk_assessment AS ra
    ON c.company_id = ra.company_id
ORDER BY c.company_name, ra.assessed_at DESC;


-- Q3. Count risk assessments for each company.
-- COUNT(ra.risk_assessment_id) returns zero when no assessment matches.
SELECT
    c.company_id,
    c.company_name,
    COUNT(ra.risk_assessment_id) AS assessment_count
FROM public.companies AS c
LEFT JOIN public.risk_assessment AS ra
    ON c.company_id = ra.company_id
GROUP BY
    c.company_id,
    c.company_name
ORDER BY assessment_count DESC, c.company_name;


-- Q4. Calculate average, minimum, and maximum risk score per company.
SELECT
    c.company_id,
    c.company_name,
    COUNT(ra.risk_assessment_id) AS assessment_count,
    ROUND(AVG(ra.risk_score), 2) AS average_risk_score,
    MIN(ra.risk_score) AS minimum_risk_score,
    MAX(ra.risk_score) AS maximum_risk_score
FROM public.companies AS c
LEFT JOIN public.risk_assessment AS ra
    ON c.company_id = ra.company_id
GROUP BY
    c.company_id,
    c.company_name
ORDER BY average_risk_score DESC NULLS LAST;


-- Q5. Count assessments grouped by company and risk level.
SELECT
    c.company_name,
    ra.risk_level,
    COUNT(*) AS assessment_count
FROM public.companies AS c
INNER JOIN public.risk_assessment AS ra
    ON c.company_id = ra.company_id
GROUP BY
    c.company_id,
    c.company_name,
    ra.risk_level
ORDER BY c.company_name, assessment_count DESC, ra.risk_level;


-- Q6. Find companies with at least three risk assessments.
-- HAVING filters groups after aggregation.
SELECT
    c.company_id,
    c.company_name,
    COUNT(ra.risk_assessment_id) AS assessment_count
FROM public.companies AS c
INNER JOIN public.risk_assessment AS ra
    ON c.company_id = ra.company_id
GROUP BY
    c.company_id,
    c.company_name
HAVING COUNT(ra.risk_assessment_id) >= 3
ORDER BY assessment_count DESC, c.company_name;


-- Q7. Find companies whose average risk score is at least 70.
SELECT
    c.company_id,
    c.company_name,
    ROUND(AVG(ra.risk_score), 2) AS average_risk_score
FROM public.companies AS c
INNER JOIN public.risk_assessment AS ra
    ON c.company_id = ra.company_id
GROUP BY
    c.company_id,
    c.company_name
HAVING AVG(ra.risk_score) >= 70
ORDER BY average_risk_score DESC;


-- Q8. Summarize high and critical assessments per company.
SELECT
    c.company_id,
    c.company_name,
    COUNT(*) AS high_or_critical_count,
    ROUND(AVG(ra.risk_score), 2) AS average_high_or_critical_score,
    MAX(ra.risk_score) AS highest_risk_score
FROM public.companies AS c
INNER JOIN public.risk_assessment AS ra
    ON c.company_id = ra.company_id
WHERE ra.risk_level IN ('HIGH', 'CRITICAL')
GROUP BY
    c.company_id,
    c.company_name
ORDER BY high_or_critical_count DESC, highest_risk_score DESC;


-- Q9. Join companies with their financial records.
-- A LEFT JOIN includes companies without financial records.
SELECT
    c.company_id,
    c.company_name,
    fr.fiscal_year,
    fr.revenue,
    fr.net_profit,
    fr.total_assets,
    fr.total_liabilities,
    fr.total_debt,
    fr.shareholders_equity,
    fr.operating_cash_flow
FROM public.companies AS c
LEFT JOIN public.financial_records AS fr
    ON c.company_id = fr.company_id
ORDER BY c.company_name, fr.fiscal_year DESC NULLS LAST;


-- Q10. Calculate financial totals per company.
-- SUM ignores NULL values; totals remain NULL when there are no records.
SELECT
    c.company_id,
    c.company_name,
    COUNT(fr.financial_record_id) AS financial_record_count,
    SUM(fr.revenue) AS total_recorded_revenue,
    SUM(fr.net_profit) AS total_recorded_net_profit,
    SUM(fr.total_assets) AS total_recorded_assets,
    SUM(fr.total_debt) AS total_recorded_debt
FROM public.companies AS c
LEFT JOIN public.financial_records AS fr
    ON c.company_id = fr.company_id
GROUP BY
    c.company_id,
    c.company_name
ORDER BY total_recorded_revenue DESC NULLS LAST;


-- Q11. Count companies represented in each risk level.
SELECT
    ra.risk_level,
    COUNT(DISTINCT ra.company_id) AS company_count,
    COUNT(*) AS assessment_count,
    ROUND(AVG(ra.risk_score), 2) AS average_risk_score
FROM public.risk_assessment AS ra
GROUP BY ra.risk_level
ORDER BY company_count DESC, ra.risk_level;


-- Q12. Find companies whose highest recorded risk score is at least 80.
SELECT
    c.company_id,
    c.company_name,
    MAX(ra.risk_score) AS highest_risk_score,
    COUNT(ra.risk_assessment_id) AS assessment_count
FROM public.companies AS c
INNER JOIN public.risk_assessment AS ra
    ON c.company_id = ra.company_id
GROUP BY
    c.company_id,
    c.company_name
HAVING MAX(ra.risk_score) >= 80
ORDER BY highest_risk_score DESC, c.company_name;
