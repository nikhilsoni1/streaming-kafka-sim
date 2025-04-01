{{ config(
    materialized = 'table',
) }}

WITH cte1 AS (
    SELECT 
        CASE 
            WHEN ed.ver_sw_release = '' THEN '<BLANK>'
            ELSE ed.ver_sw_release 
        END AS ver_sw_release,
        COUNT(ed.log_id) AS row_cnt
    FROM {{ ref('eda_dbinfo') }} ed
    GROUP BY 
        CASE 
            WHEN ed.ver_sw_release = '' THEN '<BLANK>'
            ELSE ed.ver_sw_release 
        END
),
cte2 AS (
    SELECT 
        ver_sw_release,
        row_cnt,
        SUM(row_cnt) OVER () AS num_logs
    FROM cte1
),
cte3 AS (
    SELECT 
        ver_sw_release,
        row_cnt,
        SUM(CAST(row_cnt AS FLOAT) / num_logs) OVER (
            ORDER BY row_cnt DESC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_contribution
    FROM cte2
)
SELECT 
    ver_sw_release,
    row_cnt,
    ROUND(cumulative_contribution * 100) AS cumulative_contribution
FROM cte3
where cumulative_contribution <= 0.9
ORDER BY row_cnt DESC