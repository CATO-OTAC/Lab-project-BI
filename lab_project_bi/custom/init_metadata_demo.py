from pathlib import Path

import duckdb

if "custom" not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def init_metadata_demo(*args, **kwargs):
    sql_dir = Path("/home/src/sql")

    with duckdb.connect("/tmp/bi_metadata_screenshot.duckdb") as con:
        for filename in ("init_metadata.sql", "extend_metadata.sql"):
            con.execute((sql_dir / filename).read_text(encoding="utf-8"))

        return con.execute("""
            SELECT rule_code, violation_condition, proposed_action, decision_status
            FROM etl.dq_rule
            ORDER BY rule_code
        """).df()