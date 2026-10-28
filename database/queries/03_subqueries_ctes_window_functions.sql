
-- ============================================================
-- AEGIS: AI-Powered Financial Risk & Event Intelligence
-- File: 03_subqueries_ctes_window_functions.sql
-- Purpose: Subqueries, CTEs, and Window Functions
-- Database: PostgreSQL
-- Total: 18 read-only analytical queries
-- ============================================================

-- ============================================================
-- SECTION 1: SUBQUERIES
-- ============================================================

-- Q1. Companies whose maximum risk score exceeds the overall
-- average risk score.
SELECT
    c.company_id,
    c.company_name,
    MAX(ra.risk_score) AS max_risk_score
FROM companies c
JOIN risk_assessment ra
    ON ra.company_id = c.company_id
GROUP BY c.company_id, c.company_name
HAVING MAX(ra.risk_score) > (
    SELECT AVG(risk_score)
    FROM risk_assessment
);

-- Q2. Assessments with scores above the overall average.
SELECT
    risk_assessment_id,
    company_id,
    risk_score,
    risk_level,
    assessed_at
FROM risk_assessment
WHERE risk_score > (
    SELECT AVG(risk_score)
    FROM risk_assessment
)
ORDER BY risk_score DESC;

-- Q3. Companies having at least one CRITICAL assessment.
SELECT
    c.company_id,
    c.company_name
FROM companies c
WHERE EXISTS (
    SELECT 1
    FROM risk_assessment ra
    WHERE ra.company_id = c.company_id
      AND ra.risk_level = 'CRITICAL'
);

-- Q4. Companies that have no risk assessments.
SELECT
    c.company_id,
    c.company_name
FROM companies c
WHERE NOT EXISTS (
    SELECT 1
    FROM risk_assessment ra
    WHERE ra.company_id = c.company_id
);

-- Q5. Assessments scoring above their own company's average.
-- This is a correlated subquery.
SELECT
    ra.risk_assessment_id,
    ra.company_id,
    ra.risk_score,
    ra.risk_level
FROM risk_assessment ra
WHERE ra.risk_score > (
    SELECT AVG(ra2.risk_score)
    FROM risk_assessment ra2
    WHERE ra2.company_id = ra.company_id
)
ORDER BY ra.company_id, ra.risk_score DESC;

-- Q6. Companies with HIGH or CRITICAL assessments using IN.
SELECT
    c.company_id,
    c.company_name
FROM companies c
WHERE c.company_id IN (
    SELECT DISTINCT company_id
    FROM risk_assessment
    WHERE risk_level IN ('HIGH', 'CRITICAL')
);

-- ============================================================
-- SECTION 2: COMMON TABLE EXPRESSIONS (CTEs)
-- ============================================================

-- Q7. Calculate assessment statistics for each company.
WITH company_stats AS (
    SELECT
        company_id,
        COUNT(*) AS assessment_count,
        ROUND(AVG(risk_score), 2) AS average_risk_score,
        MAX(risk_score) AS maximum_risk_score,
        MIN(risk_score) AS minimum_risk_score
    FROM risk_assessment
    GROUP BY company_id
)
SELECT
    c.company_id,
    c.company_name,
    cs.assessment_count,
    cs.average_risk_score,
    cs.maximum_risk_score,
    cs.minimum_risk_score
FROM company_stats cs
JOIN companies c
    ON c.company_id = cs.company_id
ORDER BY cs.maximum_risk_score DESC;

-- Q8. Compare each company's average with the overall average.
WITH company_averages AS (
    SELECT
        company_id,
        AVG(risk_score) AS average_score
    FROM risk_assessment
    GROUP BY company_id
),
overall_average AS (
    SELECT AVG(risk_score) AS average_score
    FROM risk_assessment
)
SELECT
    c.company_id,
    c.company_name,
    ROUND(ca.average_score, 2) AS company_average,
    ROUND(oa.average_score, 2) AS overall_average
FROM company_averages ca
JOIN companies c
    ON c.company_id = ca.company_id
CROSS JOIN overall_average oa
WHERE ca.average_score > oa.average_score
ORDER BY ca.average_score DESC;

-- Q9. Find the latest assessment timestamp for each company.
WITH latest_times AS (
    SELECT
        company_id,
        MAX(assessed_at) AS latest_assessed_at
    FROM risk_assessment
    GROUP BY company_id
)
SELECT
    c.company_id,
    c.company_name,
    ra.risk_assessment_id,
    ra.risk_score,
    ra.risk_level,
    ra.assessed_at
FROM latest_times lt
JOIN risk_assessment ra
    ON ra.company_id = lt.company_id
   AND ra.assessed_at = lt.latest_assessed_at
JOIN companies c
    ON c.company_id = ra.company_id
ORDER BY ra.assessed_at DESC;

-- Q10. Summarize the number of assessments and average score
-- for each risk level.
WITH risk_summary AS (
    SELECT
        risk_level,
        COUNT(*) AS assessment_count,
        ROUND(AVG(risk_score), 2) AS average_score
    FROM risk_assessment
    GROUP BY risk_level
)
SELECT
    risk_level,
    assessment_count,
    average_score
FROM risk_summary
ORDER BY average_score DESC;

-- ============================================================
-- SECTION 3: WINDOW FUNCTIONS
-- ============================================================

-- Q11. Rank all assessments by risk score.
SELECT
    risk_assessment_id,
    company_id,
    risk_score,
    risk_level,
    RANK() OVER (
        ORDER BY risk_score DESC
    ) AS risk_rank
FROM risk_assessment
ORDER BY risk_rank, risk_assessment_id;

-- Q12. Compare ROW_NUMBER, RANK, and DENSE_RANK.
SELECT
    risk_assessment_id,
    risk_score,
    ROW_NUMBER() OVER (
        ORDER BY risk_score DESC, risk_assessment_id
    ) AS row_num,
    RANK() OVER (
        ORDER BY risk_score DESC
    ) AS score_rank,
    DENSE_RANK() OVER (
        ORDER BY risk_score DESC
    ) AS dense_score_rank
FROM risk_assessment
ORDER BY risk_score DESC, risk_assessment_id;

-- Q13. Rank assessments separately within each company.
SELECT
    risk_assessment_id,
    company_id,
    risk_score,
    RANK() OVER (
        PARTITION BY company_id
        ORDER BY risk_score DESC
    ) AS company_risk_rank
FROM risk_assessment
ORDER BY company_id, company_risk_rank;

-- Q14. Find the latest assessment for each company using
-- ROW_NUMBER, with a deterministic tie-breaker.
WITH ranked_assessments AS (
    SELECT
        ra.*,
        ROW_NUMBER() OVER (
            PARTITION BY company_id
            ORDER BY assessed_at DESC, risk_assessment_id DESC
        ) AS row_num
    FROM risk_assessment ra
)
SELECT
    c.company_id,
    c.company_name,
    r.risk_assessment_id,
    r.risk_score,
    r.risk_level,
    r.assessed_at
FROM ranked_assessments r
JOIN companies c
    ON c.company_id = r.company_id
WHERE r.row_num = 1
ORDER BY r.assessed_at DESC;

-- Q15. Compare each assessment with the previous assessment
-- for the same company using LAG.
SELECT
    risk_assessment_id,
    company_id,
    assessed_at,
    risk_score,
    LAG(risk_score) OVER (
        PARTITION BY company_id
        ORDER BY assessed_at, risk_assessment_id
    ) AS previous_risk_score,
    risk_score - LAG(risk_score) OVER (
        PARTITION BY company_id
        ORDER BY assessed_at, risk_assessment_id
    ) AS score_change
FROM risk_assessment
ORDER BY company_id, assessed_at, risk_assessment_id;

-- Q16. Display the next assessment score using LEAD.
SELECT
    risk_assessment_id,
    company_id,
    assessed_at,
    risk_score,
    LEAD(risk_score) OVER (
        PARTITION BY company_id
        ORDER BY assessed_at, risk_assessment_id
    ) AS next_risk_score
FROM risk_assessment
ORDER BY company_id, assessed_at, risk_assessment_id;

-- Q17. Calculate the running average score per company.
SELECT
    risk_assessment_id,
    company_id,
    assessed_at,
    risk_score,
    ROUND(
        AVG(risk_score) OVER (
            PARTITION BY company_id
            ORDER BY assessed_at, risk_assessment_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS running_average_score
FROM risk_assessment
ORDER BY company_id, assessed_at, risk_assessment_id;

-- Q18. Show each assessment alongside the company's overall
-- average and difference from that average.
SELECT
    risk_assessment_id,
    company_id,
    risk_score,
    ROUND(
        AVG(risk_score) OVER (
            PARTITION BY company_id
        ),
        2
    ) AS company_average_score,
    ROUND(
        risk_score - AVG(risk_score) OVER (
            PARTITION BY company_id
        ),
        2
    ) AS difference_from_company_average
FROM risk_assessment
ORDER BY company_id, assessed_at, risk_assessment_id;

-- ============================================================
-- END OF FILE
-- ============================================================
