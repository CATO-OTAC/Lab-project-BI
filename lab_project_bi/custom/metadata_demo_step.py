from pathlib import Path
import hashlib

import duckdb

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def run_metadata_demo(*args, **kwargs):
    relative_path = (
        "Yellow Taxi Trip Record Data/2024/yellow_tripdata_2024-01.parquet"
    )
    parquet = Path("/home/src/dataset") / relative_path
    checksum = hashlib.sha256(parquet.read_bytes()).hexdigest()

    with duckdb.connect("/tmp/bi_metadata_screenshot.duckdb") as con:
        previous = con.execute("""
            SELECT file_sha256
            FROM etl.loaded_files
            WHERE source_name = 'yellow_taxi_trips' AND source_file = ?
        """, [relative_path]).fetchone()

        if previous is None:
            con.execute("BEGIN")
            try:
                con.execute("""
                    CREATE TABLE staging_demo AS
                    SELECT * FROM read_parquet(?)
                """, [str(parquet)])
                rows = con.execute(
                    "SELECT count(*) FROM staging_demo"
                ).fetchone()[0]

                con.execute("""
                    INSERT INTO etl.loaded_files
                        (source_name, source_file, file_sha256, rows_loaded)
                    VALUES ('yellow_taxi_trips', ?, ?, ?)
                """, [relative_path, checksum, rows])

                con.execute("""
                    INSERT INTO etl.event_log
                        (run_id, flow_code, result, rows_affected)
                    VALUES ('demo-2024-01', 'trip_to_stage', 'success', ?)
                """, [rows])
                con.execute("COMMIT")
            except Exception:
                con.execute("ROLLBACK")
                raise
        elif previous[0] == checksum:
            print("SKIP: Tệp đã nạp và SHA-256 trùng.")
        else:
            raise ValueError("Tệp đã đổi nội dung. Cần xác nhận cách nạp lại.")

        return con.execute("""
            SELECT run_id, flow_code, result, rows_affected, logged_at
            FROM etl.event_log
            WHERE run_id = 'demo-2024-01'
        """).df()