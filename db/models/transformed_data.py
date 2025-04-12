from sqlalchemy import BigInteger, Column, Date, DateTime, Double, Integer, MetaData, Numeric, Table, Text
from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData()


t_clean_dbinfo = Table(
    'clean_dbinfo', metadata,
    Column('updated_at_utc', DateTime),
    Column('type', Text),
    Column('log_id', Text),
    Column('rating', Text),
    Column('source', Text),
    Column('sys_hw', Text),
    Column('ver_sw', Text),
    Column('feedback', Text),
    Column('log_date', Date),
    Column('mav_type', Text),
    Column('estimator', Text),
    Column('video_url', Text),
    Column('duration_s', Double(53)),
    Column('wind_speed', Double(53)),
    Column('description', Text),
    Column('error_labels', JSONB),
    Column('flight_modes', JSONB),
    Column('vehicle_name', Text),
    Column('vehicle_uuid', Text),
    Column('airframe_name', Text),
    Column('airframe_type', Text),
    Column('ver_sw_release', Text),
    Column('sys_autostart_id', Text),
    Column('num_logged_errors', Integer),
    Column('num_logged_warnings', Integer),
    Column('flight_mode_durations', JSONB),
    schema='transformed_data'
)


t_dbinfo_sample_1k = Table(
    'dbinfo_sample_1k', metadata,
    Column('updated_at_utc', DateTime),
    Column('type', Text),
    Column('log_id', Text),
    Column('rating', Text),
    Column('source', Text),
    Column('sys_hw', Text),
    Column('ver_sw', Text),
    Column('feedback', Text),
    Column('log_date', Date),
    Column('mav_type', Text),
    Column('estimator', Text),
    Column('video_url', Text),
    Column('duration_s', Double(53)),
    Column('wind_speed', Double(53)),
    Column('description', Text),
    Column('error_labels', JSONB),
    Column('flight_modes', JSONB),
    Column('vehicle_name', Text),
    Column('vehicle_uuid', Text),
    Column('airframe_name', Text),
    Column('airframe_type', Text),
    Column('ver_sw_release', Text),
    Column('sys_autostart_id', Text),
    Column('num_logged_errors', Integer),
    Column('num_logged_warnings', Integer),
    Column('flight_mode_durations', JSONB),
    schema='transformed_data'
)


t_distinct_ver_sw_release = Table(
    'distinct_ver_sw_release', metadata,
    Column('ver_sw_release', Text),
    Column('row_cnt', BigInteger),
    Column('cumulative_contribution', Double(53)),
    schema='transformed_data'
)


t_eda_dbinfo = Table(
    'eda_dbinfo', metadata,
    Column('updated_at_utc', DateTime),
    Column('type', Text),
    Column('log_id', Text),
    Column('rating', Text),
    Column('source', Text),
    Column('sys_hw', Text),
    Column('ver_sw', Text),
    Column('feedback', Text),
    Column('log_date', Date),
    Column('mav_type', Text),
    Column('estimator', Text),
    Column('video_url', Text),
    Column('duration_s', Double(53)),
    Column('wind_speed', Double(53)),
    Column('description', Text),
    Column('error_labels', JSONB),
    Column('flight_modes', JSONB),
    Column('vehicle_name', Text),
    Column('vehicle_uuid', Text),
    Column('airframe_name', Text),
    Column('airframe_type', Text),
    Column('ver_sw_release', Text),
    Column('sys_autostart_id', Text),
    Column('num_logged_errors', Integer),
    Column('num_logged_warnings', Integer),
    Column('flight_mode_durations', JSONB),
    schema='transformed_data'
)


t_sample_pop_comp = Table(
    'sample_pop_comp', metadata,
    Column('rating', Text),
    Column('mav_type', Text),
    Column('ver_sw_release', Text),
    Column('row_count_sampled', BigInteger),
    Column('c_sampled', Numeric),
    Column('row_count_population', BigInteger),
    Column('c', Numeric),
    schema='transformed_data'
)

