{{ config(
    materialized = 'table',
) }}

-- Model: transformed_flight_logs
-- Purpose: Parse, flatten, and deduplicate raw JSON flight logs from dbinfo.raw_dbinfo

WITH cte1 AS (
    SELECT json_array_elements(rd.raw_json::json) AS raw_json
    FROM {{ source('dbinfo', 'raw_dbinfo') }} rd
),
cte2 AS (
    SELECT
        raw_json->>'type'                            AS type,
        raw_json->>'log_id'                          AS log_id,
        raw_json->>'rating'                          AS rating,
        raw_json->>'source'                          AS source,
        raw_json->>'sys_hw'                          AS sys_hw,
        raw_json->>'ver_sw'                          AS ver_sw,
        raw_json->>'feedback'                        AS feedback,
        (raw_json->>'log_date')::date                AS log_date,
        raw_json->>'mav_type'                        AS mav_type,
        raw_json->>'estimator'                       AS estimator,
        raw_json->>'video_url'                       AS video_url,
        NULLIF(raw_json->>'duration_s', '')::float   AS duration_s,
        NULLIF(raw_json->>'wind_speed', '')::float   AS wind_speed,
        raw_json->>'description'                     AS description,
        (raw_json->'error_labels')::jsonb            AS error_labels,
        (raw_json->'flight_modes')::jsonb            AS flight_modes,
        raw_json->>'vehicle_name'                    AS vehicle_name,
        raw_json->>'vehicle_uuid'                    AS vehicle_uuid,
        raw_json->>'airframe_name'                   AS airframe_name,
        raw_json->>'airframe_type'                   AS airframe_type,
        raw_json->>'ver_sw_release'                  AS ver_sw_release,
        raw_json->>'sys_autostart_id'                AS sys_autostart_id,
        NULLIF(raw_json->>'num_logged_errors', '')::integer     AS num_logged_errors,
        NULLIF(raw_json->>'num_logged_warnings', '')::integer   AS num_logged_warnings,
        (raw_json->'flight_mode_durations')::jsonb   AS flight_mode_durations,
        NOW() AT TIME ZONE 'UTC'                     AS updated_at_utc
    FROM cte1
)
SELECT DISTINCT ON (log_id)
    updated_at_utc,
    type,
    log_id,
    rating,
    source,
    sys_hw,
    ver_sw,
    REPLACE(feedback, '[__BAD_CHAR__]', ' ')     AS feedback,
    log_date,
    mav_type,
    estimator,
    video_url,
    duration_s,
    wind_speed,
    description,
    error_labels,
    flight_modes,
    vehicle_name,
    vehicle_uuid,
    airframe_name,
    airframe_type,
    ver_sw_release,
    sys_autostart_id,
    num_logged_errors,
    num_logged_warnings,
    flight_mode_durations
FROM cte2
