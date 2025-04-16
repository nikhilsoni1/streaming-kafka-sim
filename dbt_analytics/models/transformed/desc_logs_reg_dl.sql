{{ config(
    materialized = 'view',
) }}

with c1 as (
SELECT 
  (log_ts_utc AT TIME ZONE 'UTC') AT TIME ZONE 'PST' AS log_ts_pst,
  log_ts_utc,
  job_id,
  count(distinct log_id) as logs_count,
  min(ldr.file_size_bytes) / (1024*1024) as min_mb,
  percentile_cont(0.25) WITHIN GROUP (ORDER BY ldr.file_size_bytes) / (1024*1024) AS p25_mb,
  percentile_cont(0.5) WITHIN GROUP (ORDER BY ldr.file_size_bytes) / (1024*1024) AS p50_mb,
  percentile_cont(0.75) WITHIN GROUP (ORDER BY ldr.file_size_bytes) / (1024*1024) AS p75_mb,
  max(ldr.file_size_bytes) / (1024*1024) as max_mb
FROM 
  {{ source('registry', 'logs_dl_reg') }} ldr
 group by 1,2,3
)
select log_ts_pst
, log_ts_utc
, job_id
, logs_count
, round(min_mb) as min_mb
, round(c1.p25_mb) as p25_mb
, round(c1.p50_mb) as p50_mb
, round(c1.p75_mb) as p75_mb
, round(c1.max_mb) as max_mb
from c1
order by 1 desc
