{{ config(
    materialized = 'table',
) }}

SELECT 
    updated_at_utc,
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
FROM 
    {{ ref('clean_dbinfo') }} AS cd
WHERE 
    DATE_TRUNC('year', cd.log_date::timestamp WITHOUT TIME ZONE)::date > TO_DATE('2021-01-01', 'YYYY-MM-DD')
