BEGIN TRANSACTION;

CREATE SCHEMA IF NOT EXISTS etl;

CREATE TABLE IF NOT EXISTS etl.data_flow (
    flow_code VARCHAR PRIMARY KEY,
    source_name VARCHAR NOT NULL,
    destination VARCHAR NOT NULL,
    load_type VARCHAR NOT NULL CHECK (load_type IN ('file_incremental', 'full_refresh', 'to_confirm'))
);

CREATE TABLE IF NOT EXISTS etl.dq_rule (
    rule_code VARCHAR PRIMARY KEY,
    flow_code VARCHAR NOT NULL REFERENCES etl.data_flow (flow_code),
    violation_condition VARCHAR NOT NULL,
    proposed_action VARCHAR NOT NULL,
    decision_status VARCHAR NOT NULL CHECK (decision_status IN ('documented', 'to_confirm'))
);

CREATE TABLE IF NOT EXISTS etl.event_log (
    event_id UUID PRIMARY KEY DEFAULT uuid(),
    run_id VARCHAR NOT NULL,
    flow_code VARCHAR NOT NULL REFERENCES etl.data_flow (flow_code),
    rule_code VARCHAR REFERENCES etl.dq_rule (rule_code),
    logged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    result VARCHAR NOT NULL CHECK (result IN ('started', 'success', 'failed', 'warning')),
    rows_affected BIGINT CHECK (rows_affected >= 0),
    message VARCHAR
);

-- Proposed flow names and Staging targets from Metadata_Mapping.xlsx.
INSERT INTO etl.data_flow (flow_code, source_name, destination, load_type)
VALUES
    ('trip_to_stage', 'yellow_taxi_trips', 'stage.stg_yellow_taxi_trips', 'file_incremental'),
    ('lookup_to_stage', 'taxi_zone_lookup', 'stage.stg_taxi_zone_lookup', 'to_confirm'),
    ('boundary_to_stage', 'taxi_zone_boundary', 'stage.stg_taxi_zone_boundary', 'to_confirm'),
    ('stage_to_dds', 'stage', 'DDS fact and dimensions', 'to_confirm')
ON CONFLICT (flow_code) DO NOTHING;

INSERT INTO etl.dq_rule (rule_code, flow_code, violation_condition, proposed_action, decision_status)
VALUES
    ('TRIP_PERIOD', 'trip_to_stage', 'Pickup nằm ngoài giai đoạn 2024–2025',
     'Loại khỏi phạm vi nạp đã mô tả trong báo cáo nhóm', 'documented'),
    ('PASSENGER_UNKNOWN', 'trip_to_stage', 'passenger_count NULL hoặc bằng 0',
     'Giữ chuyến, xếp nhóm Unknown', 'documented'),
    ('TRIP_OUTLIER', 'trip_to_stage', 'Thời lượng, tốc độ hoặc cự ly vượt ngưỡng nghiệp vụ',
     'Gắn cờ is_outlier_trip; chốt ngưỡng và bộ lọc chỉ số trước khi áp dụng', 'to_confirm'),
    ('NEGATIVE_AMOUNT', 'trip_to_stage', 'fare_amount hoặc total_amount âm',
     'Gắn cờ is_negative_amount; chờ chốt cách tổng hợp doanh thu', 'to_confirm'),
    ('LOCATION_LOOKUP', 'stage_to_dds', 'Mã đón hoặc trả không tra được trong Dim_Location',
     'Dùng khóa Unknown (-1) cho mã không tra được; giữ riêng mã nguồn 264/265', 'documented')
ON CONFLICT (rule_code) DO NOTHING;

COMMIT;
