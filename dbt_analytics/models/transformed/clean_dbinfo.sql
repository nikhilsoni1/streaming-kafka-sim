{{ config(
    materialized = 'table',
) }}

-- Model: transformed_flight_logs
-- Purpose: Parse, flatten, and deduplicate raw JSON flight logs from dbinfo.raw_dbinfo

WITH cte1 AS (
    SELECT 
        type,
        log_id,
        rating,
        source,
        sys_hw,
        ver_sw,
        feedback,
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
        flight_mode_durations,
        DENSE_RANK() OVER (
            PARTITION BY log_id 
            ORDER BY log_ts_utc DESC
        ) AS rnk
    FROM {{ source('dbinfo', 'raw_dbinfo') }} rd
)

SELECT 
    type,
    log_id,
    rating,
    source,
    sys_hw,
    ver_sw,
    feedback,
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
FROM cte1
WHERE rnk = 1