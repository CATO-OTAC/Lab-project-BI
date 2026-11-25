import hashlib
from pathlib import Path

import duckdb
import pandas as pd

if "custom" not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def test_metadata_real(*args, **kwargs):
    root = Path("/home/src")
    source = "yellow_taxi_trips"
    relative_path = (
        "Yellow Taxi Trip Record Data/2024/yellow_tripdata_2024-01.parquet"
    )
    parquet = root / "dataset" / relative_path

    if not parquet.is_file():
        raise FileNotFoundError(f"Không tìm thấy file Parquet: {parquet}")

    sql_files = ("init_metadata.sql", "extend_metadata.sql")
    insert_file_sql = """
        INSERT INTO etl.loaded_files
            (source_name, source_file, file_sha256, rows_loaded)
        VALUES (?, ?, ?, ?)
    """
    results = []

    with duckdb.connect(":memory:") as con:
        # Ca 1: Chạy hai script hai lần và kiểm tra số bản ghi.
        for _ in range(2):
            for filename in sql_files:
                sql = (root / "sql" / filename).read_text(encoding="utf-8")
                con.execute(sql)

        counts = con.execute("""
            SELECT
                (SELECT count(*) FROM etl.metadata),
                (SELECT count(*) FROM etl.metadata
                 WHERE lset IS NULL AND cet IS NULL),
                (SELECT count(*) FROM etl.data_flow),
                (SELECT count(*) FROM etl.dq_rule),
                (SELECT count(*) FROM etl.loaded_files),
                (SELECT count(*) FROM etl.event_log)
        """).fetchone()

        assert counts == (3, 3, 4, 5, 0, 0), counts
        results.append((
            1, "Khởi tạo hai lần", "PASS",
            "3 nguồn, 4 luồng, 5 quy tắc. Chưa có tệp đã nạp hoặc log."
        ))

        # Ca 2: Nạp toàn bộ Parquet thật và ghi metadata trong cùng giao dịch.
        digest = hashlib.sha256()
        with parquet.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        checksum = digest.hexdigest()

        con.execute("BEGIN")
        try:
            con.execute("""
                CREATE TABLE staging_test AS
                SELECT * FROM read_parquet(?)
            """, [str(parquet)])

            rows = con.execute(
                "SELECT count(*) FROM staging_test"
            ).fetchone()[0]
            assert rows > 0, "Tệp không có dòng dữ liệu."

            con.execute(insert_file_sql, [source, relative_path, checksum, rows])
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise

        staged = con.execute("SELECT count(*) FROM staging_test").fetchone()
        saved = con.execute("""
            SELECT file_sha256, rows_loaded
            FROM etl.loaded_files
            WHERE source_name = ? AND source_file = ?
        """, [source, relative_path]).fetchone()

        assert staged == (rows,), staged
        assert saved == (checksum, rows), saved
        results.append((
            2, "COMMIT dữ liệu thật", "PASS",
            f"Staging có {rows} dòng và metadata khớp SHA-256."
        ))

        # Ca 3: Thêm một chuyến thật rồi cố ý vi phạm CHECK rows_loaded >= 0.
        failed_key = "test/rollback-2024-01.parquet"
        con.execute("BEGIN")
        try:
            con.execute("""
                INSERT INTO staging_test
                SELECT * FROM read_parquet(?) LIMIT 1
            """, [str(parquet)])
            con.execute(insert_file_sql, [source, failed_key, checksum, -1])
        except duckdb.ConstraintException as exc:
            failure_message = str(exc)
            con.execute("ROLLBACK")
        except Exception:
            con.execute("ROLLBACK")
            raise
        else:
            con.execute("ROLLBACK")
            raise AssertionError("DuckDB phải từ chối rows_loaded = -1.")

        staged_after_rollback = con.execute(
            "SELECT count(*) FROM staging_test"
        ).fetchone()
        failed_files = con.execute("""
            SELECT count(*)
            FROM etl.loaded_files
            WHERE source_name = ? AND source_file = ?
        """, [source, failed_key]).fetchone()

        assert staged_after_rollback == (rows,), staged_after_rollback
        assert failed_files == (0,), failed_files
        results.append((
            3, "ROLLBACK khi nạp lỗi", "PASS",
            f"Staging vẫn có {rows} dòng. Lượt lỗi không có bản ghi tệp."
        ))

        # Ca 4: Ghi và đọc lại lỗi sau khi đã hoàn tác giao dịch nạp.
        con.execute("""
            INSERT INTO etl.event_log (run_id, flow_code, result, message)
            VALUES ('test-real-rollback', 'trip_to_stage', 'failed', ?)
        """, [failure_message])

        logged = con.execute("""
            SELECT flow_code, result, message
            FROM etl.event_log
            WHERE run_id = 'test-real-rollback'
        """).fetchone()

        assert logged == ("trip_to_stage", "failed", failure_message), logged
        results.append((
            4, "Ghi log sau ROLLBACK", "PASS",
            "Đọc lại được trạng thái failed và thông báo lỗi DuckDB."
        ))

    return pd.DataFrame(
        results,
        columns=["ca", "tinh_huong", "ket_qua", "chi_tiet"],
    )