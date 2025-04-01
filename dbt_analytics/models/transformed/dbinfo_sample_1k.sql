{{ config(
    materialized = 'table',
) }}

WITH stratum_counts AS (
    SELECT rating
    , mav_type
    , ver_sw_release
    , COUNT(*) AS total_rows
    FROM {{ ref('eda_dbinfo') }} ed
    WHERE ed.ver_sw_release IN (
        SELECT ver_sw_release
        FROM transformed_data.distinct_ver_sw_release
        WHERE cumulative_contribution >= 0.75
    )
    GROUP BY rating, mav_type, ver_sw_release
),
total_count AS (
    SELECT SUM(total_rows) AS total_rows_all FROM stratum_counts
),
sampling_plan AS (
    SELECT 
        sc.rating,
        sc.mav_type,
        sc.ver_sw_release,
        CEIL((sc.total_rows * 1000.0) / tc.total_rows_all)::INT AS target_sample_size
    FROM stratum_counts sc, total_count tc
)
SELECT ed.*
FROM sampling_plan sp
JOIN LATERAL (
    SELECT * FROM {{ ref('eda_dbinfo') }} ed1
    WHERE ed1.rating = sp.rating
      AND ed1.mav_type = sp.mav_type
      AND ed1.ver_sw_release = sp.ver_sw_release
    ORDER BY RANDOM()
    LIMIT sp.target_sample_size
) ed ON true