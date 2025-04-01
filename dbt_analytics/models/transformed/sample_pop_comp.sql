{{
    config(
        materialized = 'table',
    )
}}

WITH sample_counts AS (
    SELECT 
        s.rating,
        s.mav_type,
        s.ver_sw_release,
        COUNT(DISTINCT s.log_id) AS row_count
    FROM {{ ref('dbinfo_sample_1k') }} s
    GROUP BY s.rating, s.mav_type, s.ver_sw_release
),
sample_distribution AS (
    SELECT 
        sc.rating,
        sc.mav_type,
        sc.ver_sw_release,
        sc.row_count,
        sc.row_count * 1.0 / SUM(sc.row_count) OVER () AS c_sampled
    FROM sample_counts sc
),
population_counts AS (
    SELECT 
        ed.rating,
        ed.mav_type,
        ed.ver_sw_release,
        COUNT(DISTINCT ed.log_id) AS row_count
    FROM {{ ref('eda_dbinfo') }} ed
    GROUP BY ed.rating, ed.mav_type, ed.ver_sw_release
),
population_distribution AS (
    SELECT 
        pc.rating,
        pc.mav_type,
        pc.ver_sw_release,
        pc.row_count,
        pc.row_count * 1.0 / SUM(pc.row_count) OVER () AS c
    FROM population_counts pc
)
SELECT 
    sd.rating,
    sd.mav_type,
    sd.ver_sw_release,
    sd.row_count AS row_count_sampled,
    sd.c_sampled,
    pd.row_count AS row_count_population,
    pd.c
FROM sample_distribution sd
JOIN population_distribution pd 
    ON sd.rating = pd.rating
   AND sd.mav_type = pd.mav_type
   AND sd.ver_sw_release = pd.ver_sw_release
   order by 6 desc