BEGIN TRANSACTION;

CREATE SCHEMA IF NOT EXISTS etl;

CREATE TABLE IF NOT EXISTS etl.metadata (
    source_name VARCHAR PRIMARY KEY,
    lset TIMESTAMPTZ,
    cet TIMESTAMPTZ
);

INSERT INTO etl.metadata (source_name)
VALUES
    ('yellow_taxi_trips'),
    ('taxi_zone_lookup'),
    ('taxi_zone_boundary')
ON CONFLICT (source_name) DO NOTHING;

CREATE TABLE IF NOT EXISTS etl.loaded_files (
    source_name VARCHAR NOT NULL REFERENCES etl.metadata (source_name),
    source_file VARCHAR NOT NULL,
    file_sha256 VARCHAR NOT NULL CHECK (length(file_sha256) = 64),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    rows_loaded BIGINT NOT NULL CHECK (rows_loaded >= 0),
    PRIMARY KEY (source_name, source_file)
);

COMMIT;
