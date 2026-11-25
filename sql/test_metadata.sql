.bail on
.read init_metadata.sql
.read extend_metadata.sql

SELECT CASE WHEN
    (SELECT count(*) FROM etl.metadata WHERE lset IS NULL AND cet IS NULL) = 3
    AND (SELECT count(*) FROM etl.loaded_files) = 0
    AND (SELECT count(*) FROM etl.data_flow) = 4
    AND (SELECT count(*) FROM etl.dq_rule) = 5
    AND (SELECT count(*) FROM etl.event_log) = 0
    THEN 'PASS 1: Initialization and repeated execution'
    ELSE error('Unexpected initial metadata')
END AS test_result;

CREATE TEMP TABLE staging_demo (source_file VARCHAR, trip_id INTEGER);
BEGIN;
INSERT INTO staging_demo VALUES ('2024-01.parquet', 1);
INSERT INTO etl.loaded_files (source_name, source_file, file_sha256, rows_loaded)
VALUES ('yellow_taxi_trips', '2024-01.parquet', repeat('a', 64), 1);
COMMIT;

SELECT CASE WHEN
    (SELECT count(*) FROM staging_demo WHERE source_file = '2024-01.parquet') = 1
    AND (SELECT count(*) FROM etl.loaded_files
         WHERE source_name = 'yellow_taxi_trips' AND source_file = '2024-01.parquet'
           AND file_sha256 = repeat('a', 64) AND rows_loaded = 1) = 1
    THEN 'PASS 2: Committed staging row and matching file metadata'
    ELSE error('Commit verification failed')
END AS test_result;

BEGIN;
INSERT INTO staging_demo VALUES ('2024-02.parquet', 2);
INSERT INTO etl.loaded_files (source_name, source_file, file_sha256, rows_loaded)
VALUES ('yellow_taxi_trips', '2024-02.parquet', repeat('b', 64), 1);
ROLLBACK;

SELECT CASE WHEN
    (SELECT count(*) FROM staging_demo WHERE source_file = '2024-02.parquet') = 0
    AND (SELECT count(*) FROM etl.loaded_files WHERE source_file = '2024-02.parquet') = 0
    THEN 'PASS 3: Rolled back staging row and file metadata'
    ELSE error('Rollback verification failed')
END AS test_result;

INSERT INTO etl.event_log (run_id, flow_code, result, message)
VALUES ('test-run-02', 'trip_to_stage', 'failed', 'Simulated failure');

SELECT CASE WHEN
    (SELECT count(*) FROM etl.event_log
     WHERE run_id = 'test-run-02' AND flow_code = 'trip_to_stage'
       AND result = 'failed' AND message = 'Simulated failure') = 1
    THEN 'PASS 4: Failure log recorded after rollback'
    ELSE error('Event log verification failed')
END AS test_result;
